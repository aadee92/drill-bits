import tkinter as tk
from Drawer import DrawerManager, Pocket
import csv


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Get the panel manager ready
        self.dm = DrawerManager(p_x_padding=0.125 ,
                                p_y_padding=.25 ,
                                p_x_width=9.625 ,
                                p_y_depth=15 )
        with open('DrillSizes.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Skip the header row
            next(csv_reader)
            pocket_info = [row for row in csv_reader]

        # Fill the panel manager
        for name, name_in, width, height in pocket_info:
            try:
                pocket = Pocket(float(width) , float(height) , name, name_in)
            except:
                print("Error")
            self.dm.add_pocket(pocket)

        # Main number entry field
        self.number_entry = tk.Entry(self.parent, justify='center', font=("Prusia",30))
        self.number_entry.grid(row=0, column=0, columnspan=1, sticky='we')
        self.number_entry.bind('<Return>', self.draw_drawer)

        # Main canvas we'll draw the drawer in
        self.drawer_canvas = tk.Canvas(self.parent)
        self.drawer_canvas.grid(row=1, column=0, columnspan=1, sticky='nsew')

        self.pocket_list = list()
        for drawer in self.dm.drawers:
            for panel in drawer.panels:
                for row in panel.rows:
                    for pocket in row.pockets:
                        self.pocket_list.append([float(pocket.size_in), pocket, row, panel, drawer])

    def draw_drawer(self, event=None):
        self.drawer_canvas.delete("all")
        try:
            drill_size = self.number_entry.get()
            if "in" in drill_size:
                drill_size = drill_size.split("in")[0].strip()
            elif '"' in drill_size:
                drill_size = drill_size.split('"')[0].strip()

            drill_size = float(drill_size)
        except ValueError:
            if "/" in drill_size:
                num = drill_size.split("/")[0].strip()
                den = drill_size.split("/")[1].strip()
                drill_size = float(num)/float(den)
            elif "mm" in drill_size:
                drill_size = float(drill_size.split("mm")[0].strip())/25.4
            elif "cm" in drill_size:
                drill_size = float(drill_size.split("cm")[0].strip())/2.54
            elif "#" in drill_size or len(drill_size) == 1:
                drill_size = drill_size.strip()
                for pocket in self.pocket_list:
                    if pocket[1].size == drill_size:
                        drill_size = pocket[0]
                        break

        # Closest drill bit
        closest = min(self.pocket_list, key=lambda x: abs(x[0] - drill_size))

        # Get the drawer number
        drawer_number = self.dm.drawers.index(closest[4])

        # Designate the pocket of interest
        pocket = closest[1]
        orig_bg = pocket.bg
        orig_outline = pocket.outline
        pocket.bg = '#f00'
        pocket.outline = '#00f'

        # And draw the entire drawer
        drawer = closest[4]
        drawer.draw(self.drawer_canvas)

        # And label the drawer number
        width = self.drawer_canvas.winfo_width()
        height = self.drawer_canvas.winfo_height()
        self.drawer_canvas.create_text(width/2, height/2,
                                       text=str(drawer_number+1),
                                       font=("Purisa", 300),
                                       )


        # And cleanup
        pocket.bg = orig_bg
        pocket.outline = orig_outline
        self.number_entry.delete(0, 'end')


if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen',True)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    MainApplication(root)

    root.mainloop()

