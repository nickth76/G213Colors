#!/usr/bin/env python3

# No longer needed: from __future__ import print_function
import G213Colors # Import the module
from time import sleep
import gi
import sys
import os # For path manipulation
import logging

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Configure logging (place this early)
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("g213colors_gui") # Specific logger for the GUI part

NAME = "G213 Colors"
PRODUCTS = ["G213", "G203"]
USER_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "G213Colors")

# Determine runtime options (e.g., -t for startup)
numArguments = len(sys.argv)
option = str(sys.argv[1]) if numArguments > 1 else ""


class Window(Gtk.Window):

    def btnGetHex(self, btn):
        color = btn.get_rgba()
        red = int(color.red * 255)
        green = int(color.green * 255)
        blue = int(color.blue * 255)
        hexColor = f"{red:02x}{green:02x}{blue:02x}" # Using f-string
        return hexColor

    def sbGetValue(self, sb):
        return sb.get_value_as_int()

    def _get_user_config_path(self, product_name):
        """Generates the path for a product-specific user configuration file."""
        return os.path.join(USER_CONFIG_DIR, f"{product_name}.conf")

    def sendStatic(self, product):
        logger.info(f"Initiating static color for {product}")
        controller = G213Colors.LogitechDevice(product) # Create an instance
        
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            # TODO: Show a user-facing error dialog (e.g., Gtk.MessageDialog)
            return

        color_hex = self.btnGetHex(self.staticColorButton)
        if controller.send_color_command(color_hex): # Field 0 is default for full color
            logger.info(f"Static color command sent to {product}.")
            # Construct the command string that was effectively sent
            field_for_static = 0 
            command_to_save = controller.spec["colorCommand"].format(str(format(field_for_static, '02x')), color_hex)
            
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(command_to_save, user_conf_path) # Save to user-specific file
        else:
            logger.error(f"Failed to send static color command to {product}.")
            # TODO: Show user-facing error dialog
        controller.disconnect()

    def sendBreathe(self, product):
        logger.info(f"Initiating breathe effect for {product}")
        controller = G213Colors.LogitechDevice(product)
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            return

        color_hex = self.btnGetHex(self.breatheColorButton)
        speed = self.sbGetValue(self.sbBCycle)
        if controller.send_breathe_command(color_hex, speed):
            logger.info(f"Breathe command sent to {product}.")
            command_to_save = controller.spec["breatheCommand"].format(color_hex, str(format(speed, '04x')))
            
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(command_to_save, user_conf_path)
        else:
            logger.error(f"Failed to send breathe command to {product}.")
        controller.disconnect()

    def sendCycle(self, product):
        logger.info(f"Initiating cycle effect for {product}")
        controller = G213Colors.LogitechDevice(product)
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            return

        speed = self.sbGetValue(self.sbCycle)
        if controller.send_cycle_command(speed):
            logger.info(f"Cycle command sent to {product}.")
            command_to_save = controller.spec["cycleCommand"].format(str(format(speed, '04x')))

            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(command_to_save, user_conf_path)
        else:
            logger.error(f"Failed to send cycle command to {product}.")
        controller.disconnect()

    def sendSegments(self, product):
        logger.info(f"Initiating segment colors for {product}")
        controller = G213Colors.LogitechDevice(product)
        
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            return

        commands_to_save_list = []
        all_segments_sent_successfully = True
        for i in range(1, 6): # Segments 1 to 5
            segment_color_hex = self.btnGetHex(self.segmentColorBtns[i-1])
            logger.debug(f"Sending segment {i} color {segment_color_hex} for {product}")
            if not controller.send_color_command(segment_color_hex, i): # Pass segment index as field
                logger.error(f"Failed to send color for segment {i} to {product}.")
                all_segments_sent_successfully = False
                break 
            
            command_for_segment = controller.spec["colorCommand"].format(str(format(i, '02x')), segment_color_hex)
            commands_to_save_list.append(command_for_segment)
            sleep(0.01) # Original sleep, consider if still needed with faster modern USB
        
        if all_segments_sent_successfully:
            logger.info(f"All segment commands sent to {product}.")
            full_data_to_save = "\n".join(commands_to_save_list)
            
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(full_data_to_save, user_conf_path)
        else:
            logger.warning(f"Segment color setting partially failed for {product}. Configuration not saved for this attempt.")

        controller.disconnect()

    def sendManager(self, product_target): # Renamed parameter to avoid conflict
        if product_target == "all":
            logger.info("Applying settings to all configured products.")
            for p in PRODUCTS:
                # Each product will now load its settings based on its active tab
                self.sendManager(p) # Recursive call for each product
        else:
            # product_target is a specific product name string e.g. "G213"
            self.stackName = self.stack.get_visible_child_name()
            logger.info(f"Managing {self.stackName} settings for product: {product_target}")
            if self.stackName == "static":
                self.sendStatic(product_target)
            elif self.stackName == "cycle":
                self.sendCycle(product_target)
            elif self.stackName == "breathe":
                self.sendBreathe(product_target)
            elif self.stackName == "segments":
                # Note: Segments are typically a G213 feature.
                # Consider disabling this option in the GUI if G203 is selected,
                # or ensuring PRODUCT_SPECS for G203 handles segment commands gracefully (e.g. ignore or map to full color).
                # For now, it will attempt based on G203's "colorCommand" template if called.
                if product_target == "G203":
                     logger.warning("Segment mode is typically for G213. G203 might not support distinct segments.")
                self.sendSegments(product_target)


    def on_button_clicked(self, button, product):
        # Removed unused ctime and btime globals
        logger.debug(f"Button clicked for product: {product}. Current effect tab: {self.stack.get_visible_child_name()}")
        self.sendManager(product)

    def __init__(self):
        Gtk.Window.__init__(self, title=NAME)
        self.set_border_width(10)
        # Ensure the user config directory exists on GUI startup (optional, save_configuration also does it)
        # os.makedirs(USER_CONFIG_DIR, exist_ok=True) # This is better done within save_configuration

        vBoxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(vBoxMain)

        # ... (Rest of your __init__ for GTK components remains largely the same) ...
        ###STACK
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        ###STATIC TAB
        vBoxStatic = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.staticColorButton = Gtk.ColorButton()
        vBoxStatic.add(self.staticColorButton)
        self.stack.add_titled(vBoxStatic, "static", "Static")

        ###CYCLE TAB
        vBoxCycle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.adjCycle = Gtk.Adjustment(5000, 500, 65535, 100, 100, 0)
        self.sbCycle = Gtk.SpinButton()
        self.sbCycle.set_adjustment(self.adjCycle)
        vBoxCycle.add(self.sbCycle)
        self.stack.add_titled(vBoxCycle, "cycle", "Cycle")

        ###BREATHE TAB
        vBoxBreathe = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.breatheColorButton = Gtk.ColorButton()
        vBoxBreathe.add(self.breatheColorButton)
        self.adjBCycle = Gtk.Adjustment(5000, 500, 65535, 100, 100, 0)
        self.sbBCycle = Gtk.SpinButton()
        self.sbBCycle.set_adjustment(self.adjBCycle)
        vBoxBreathe.add(self.sbBCycle)
        self.stack.add_titled(vBoxBreathe, "breathe", "Breathe")

        ###SEGMENTS TAB
        hBoxSegments = Gtk.Box(spacing=5)
        self.segmentColorBtns = [Gtk.ColorButton() for _ in range(5)]
        for btn in self.segmentColorBtns:
            hBoxSegments.pack_start(btn, True, True, 0)
        self.stack.add_titled(hBoxSegments, "segments", "Segments")

        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        vBoxMain.pack_start(self.stack_switcher, True, True, 0)
        vBoxMain.pack_start(self.stack, True, True, 0)

        hBoxSetButtons = Gtk.Box(spacing=5)
        self.setColorBtns = [] # This list doesn't seem to be used later, can be local var
        for p in PRODUCTS:
            btn = Gtk.Button.new_with_label("Set " + p) # Consider f-string: f"Set {p}"
            hBoxSetButtons.pack_start(btn, True, True, 0)
            btn.connect("clicked", self.on_button_clicked, p)
        vBoxMain.pack_start(hBoxSetButtons, True, True, 0)

        btnSetAll = Gtk.Button.new_with_label("Set all")
        btnSetAll.connect("clicked", self.on_button_clicked, "all")
        vBoxMain.pack_start(btnSetAll, True, True, 0)


# Startup logic (for -t option)
if option == "-t": # Use '==' for string comparison
    logger.info("Startup option '-t' detected. Applying system default saved settings.")
    # The systemd service will try to load from the system-wide default config file.
    # This file should be manually created or managed by an admin if system-wide
    # startup settings are desired, as the GUI now saves to user-specific files.
    # The LogitechDevice.SYSTEM_DEFAULT_CONF_FILE is /etc/G213Colors.conf
    success = G213Colors.LogitechDevice.apply_configuration_from_file(G213Colors.LogitechDevice.SYSTEM_DEFAULT_CONF_FILE)
    if success:
        logger.info("System default settings applied successfully via -t.")
        sys.exit(0)
    else:
        logger.error("Failed to apply system default settings via -t.")
        sys.exit(1) # Exit with error code

# Main application entry point
if __name__ == "__main__":
    if not option:  # Only launch GUI if no other option like -t is given
        logger.info("Launching G213Colors GUI.")
        try:
            win = Window()
            win.connect("delete-event", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        except Exception as e: # Catch any unexpected error during GUI startup
            logger.critical(f"Critical error launching GUI: {e}", exc_info=True)
            # Fallback to console message if Gtk can't show error
            print(f"Critical error launching GUI: {e}", file=sys.stderr)
            sys.exit(1)
    elif option and option != "-t": # If option is given but it's not -t
        logger.warning(f"Unknown option provided: {option}")
        print(f"Unknown option: {option}. Use '-t' for applying system default config at startup, or no option for GUI.", file=sys.stderr)
        sys.exit(1)
