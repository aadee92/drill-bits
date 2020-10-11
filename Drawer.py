import tkinter as tk
SCALE = 60


class Pocket:
    def __init__(self, width, height, size, size_in):
        self.width = width
        self.height = height
        self.size = size
        self.size_in = size_in
        self.bg = '#fff'
        self.outline = '#000'

    def width_adjust(self, width):
        self.width = width

    def height_adjust(self, height):
        self.height_adjust = height

class Row:
    pockets = list()

    def __init__(self, x_width, x_padding):
        self.x_padding = x_padding
        self.x_width = x_width
        self.pockets = list()

    def add_pocket(self, pocket):
        if (self.pocket_width_sum + pocket.width + self.x_padding) >= self.x_width:
            # There was no more room in the row to add another pocket.
            # Now, let's scale each pocket width enough to even everything out.
            paddings = len(self.pockets) + 1
            scale_factor = (self.x_width - (self.x_padding*paddings)) / (self.pocket_total_width)
            for pocket in self.pockets:
                pocket.width_adjust(pocket.width*scale_factor)
            return False
        else:
            self.pockets.append(pocket)
            self.__update_pocket_heights()
            return True

    @property
    def pocket_total_width(self):
        width_sum = 0
        for p in self.pockets:
            width_sum += p.width
        return width_sum

    @property
    def pocket_width_sum(self):
        width_sum = self.x_padding
        for p in self.pockets:
           width_sum += p.width + self.x_padding
        return width_sum

    @property
    def row_height(self):
        max_height = 0
        for p in self.pockets:
            if p.height > max_height:
                max_height = p.height
        return max_height

    def __update_pocket_heights(self):
        h = self.row_height
        for p in self.pockets:
           p.height_adjust = h


class Panel:
    rows = list()

    def __init__(self, x_padding, y_padding, x_width, y_depth):
        self.x_padding = x_padding
        self.y_padding = y_padding
        self.x_width = x_width
        self.y_depth = y_depth
        self.rows = list()
        self.rows.append(Row(self.x_width, self.x_padding))

    @property
    def row_total_height(self):
        row_sum_height = 0
        for row in self.rows:
            row_sum_height += row.row_height
        return row_sum_height

    def add_pocket(self, pocket):
        # Does it fit in the width?
        # Yes: Then is the row height still good?
        #   Yes: Add it to the row
        #   No: Try adding a new row
        # No: Can it fit in a new row
        #   Yes: Create a new row
        #   No:  Return false

        if self.rows[-1].add_pocket(pocket):
            # The pocket fits in the width
            if self.row_height_sum > self.y_depth:
                # But its too tall, so remove it from the row
                self.rows[-1].pockets.pop()
                if self.__add_row(pocket):
                    # We sucessfully added another row
                    return True
                else:
                    # Cant add it to the row, or add another row
                    return False
            else:
                # Everything is good first try
                return True
        else:
            # Doesn't fit the width, try a new row
            if self.__add_row(pocket):
                # It fit into the new row
                return True
            else:
                # It didn't fit into a new row. Time for a new panel.
                return False

    def __add_row(self, pocket):
        self.rows.append(Row(self.x_width, self.x_padding))
        self.rows[-1].add_pocket(pocket)
        if self.row_height_sum > self.y_depth:
            # we don't fit the row, remove it
            self.rows.pop()
            # And now let's extend all the pocket height's to fill in any missing space
            paddings = len(self.rows) + 1
            scale_factor = (self.y_depth - (self.y_padding*paddings)) / (self.row_total_height)
            for row in self.rows:
                # Cheap hack to adjust row height:
                row.pockets[-1].height = row.row_height*scale_factor
            return False
        else:
            return True

    def draw(self, canvas, position=0):
        canvas_width = canvas.winfo_width()
        x_y_padding = .2 # in
        SCALE = (canvas_width)/(3*self.x_width + 4*x_y_padding) # px / inch
        x_offset = position * self.x_width + (position + 1) * x_y_padding # in

        last_y = x_y_padding + self.y_padding
        x1 = x_offset
        x2 = (x1 + self.x_width)
        y1 = x_y_padding
        y2 = (y1 + self.y_depth)
        canvas.create_rectangle(x1 * SCALE, y1 * SCALE, x2 * SCALE, y2 * SCALE, fill="#CDCDCD", outline="#000")

        # Sketch the pockets
        for r, row in enumerate(self.rows):
            last_x = x_offset
            for c, pocket in enumerate(row.pockets):
                x1 = (last_x + self.x_padding)
                x2 = (x1 + pocket.width)
                y1 = (last_y)
                y2 = (y1 + row.row_height)
                canvas.create_rectangle(x1*SCALE, y1*SCALE, x2*SCALE, y2*SCALE, outline=pocket.outline, fill=pocket.bg)
                last_x = x2
                pocket.x1 = x1
                pocket.x2 = x2
                pocket.y1 = y1
                pocket.y2 = y2

                # Create sketch text input
                canvas.create_text((x1+x2)/2*SCALE, (y1+y2)/2*SCALE,
                                   text=pocket.size,
                                   width=(x2-x1)*SCALE,
                                   justify=tk.CENTER)
                #dwg.add(dwg.text(pocket.size,    insert=(x1*72, (y1-.12)*72),       fill='black', font_size='.125in'))
                #dwg.add(dwg.text(pocket.size_in, insert=(x1*72, (y1)*72), fill='black', font_size='.125in'))

            last_y = y2 + self.y_padding

    @property
    def row_height_sum(self):
            height_sum = self.y_padding# 0
            for r in self.rows:
                height_sum += r.row_height + self.y_padding
            return height_sum


class Drawer:
    def __init__(self, p_x_padding, p_y_padding, p_x_width, p_y_depth):
        self.panels = list()
        self.p_x_padding = p_x_padding
        self.p_y_padding = p_y_padding
        self.p_x_width = p_x_width
        self.p_y_depth = p_y_depth
        self.panels.append(Panel(self.p_x_padding,
                                  self.p_y_padding,
                                  self.p_x_width,
                                  self.p_y_depth))

    def add_pocket(self, pocket):
        if self.panels[-1].add_pocket(pocket):
            # panel is not full
            return True
        # panel is full. Can we add another to the drawer?
        elif len(self.panels) < 3:
            # We can add another panel to the drawer
            self.panels.append(Panel(self.p_x_padding,
                                     self.p_y_padding,
                                     self.p_x_width,
                                     self.p_y_depth))
            self.panels[-1].add_pocket(pocket)
            return True
        else:
            # No more panels fit in the drawer.
            return False

    def draw(self, canvas):
        for i, panel in enumerate(self.panels):
            panel.draw(canvas,i)


class DrawerManager:

    def __init__(self, p_x_padding, p_y_padding, p_x_width, p_y_depth):
        self.drawers = list()
        self.p_x_padding = p_x_padding
        self.p_y_padding = p_y_padding
        self.p_x_width = p_x_width
        self.p_y_depth = p_y_depth
        # Create the first drawer
        self.drawers.append(Drawer(self.p_x_padding,
                                   self.p_y_padding,
                                   self.p_x_width,
                                   self.p_y_depth)
                            )

    def add_pocket(self, pocket):
        if self.drawers[-1].add_pocket(pocket):
            # panel is not full
            return True
        else:
            # drawer is full, add another drawer
            self.drawers.append(Drawer(self.p_x_padding,
                                       self.p_y_padding,
                                       self.p_x_width,
                                       self.p_y_depth)
                                )
            self.drawers[-1].add_pocket(pocket)
            return False
