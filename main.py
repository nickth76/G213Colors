#!/usr/bin/env python3

import G213Colors # Import the module
from time import sleep
import gi
import sys
import os # For path manipulation
import logging
import argparse # For more robust argument parsing

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

# --- Command-Line Argument Parsing ---
parser = argparse.ArgumentParser(description="G213 Colors GUI and CLI tool.")
parser.add_argument(
    "-t", "--apply-system-default",
    action="store_true",
    help="Apply system-wide default configuration from /etc/G213Colors.conf and exit."
)
parser.add_argument(
    "-auc", "--apply-user-config",
    metavar="PRODUCT_NAME",
    type=str,
    choices=PRODUCTS, # Restrict to known products
    help=f"Apply user-specific saved configuration for the given PRODUCT_NAME and exit. Choices: {PRODUCTS}"
)

# Parse arguments at the start.
# This will also handle --help and exit if invalid arguments are given.
try:
    args = parser.parse_args()
except SystemExit as e:
    # argparse exits with code 0 for --help, 2 for error.
    # We want to respect that and not proceed to GUI.
    sys.exit(e.code)


# --- CLI Action: Apply System Default Config (-t) ---
if args.apply_system_default:
    logger.info("Option '-t' / '--apply-system-default' detected. Applying system default saved settings.")
    success = G213Colors.LogitechDevice.apply_configuration_from_file(
        G213Colors.LogitechDevice.SYSTEM_DEFAULT_CONF_FILE
    )
    if success:
        logger.info("System default settings applied successfully via -t.")
        sys.exit(0)
    else:
        logger.error("Failed to apply system default settings via -t.")
        sys.exit(1)

# --- CLI Action: Apply User Config (--apply-user-config) ---
elif args.apply_user_config:
    product_to_load = args.apply_user_config
    logger.info(f"Option '--apply-user-config' detected for product: {product_to_load}")
    
    user_conf_path = os.path.join(USER_CONFIG_DIR, f"{product_to_load}.conf")
    logger.info(f"Attempting to load user config from: {user_conf_path}")

    if not os.path.exists(user_conf_path):
        logger.warning(f"User configuration file not found for {product_to_load} at {user_conf_path}. Nothing to apply.")
        sys.exit(0) # Not an error, just no config to apply

    success = G213Colors.LogitechDevice.apply_configuration_from_file(user_conf_path)
    
    if success:
        logger.info(f"User settings for {product_to_load} applied successfully from {user_conf_path}.")
        sys.exit(0)
    else:
        logger.error(f"Failed to apply user settings for {product_to_load} from {user_conf_path}.")
        sys.exit(1)


# --- GUI Application Class ---
class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title=NAME)
        self.set_border_width(10)
        
        self.autostart_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
        try:
            os.makedirs(self.autostart_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Could not create autostart directory {self.autostart_dir}: {e}")
            # Non-fatal, GUI will still load, but autostart management might fail.

        vBoxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10) # Increased main spacing a bit
        self.add(vBoxMain)

        # --- STACK for different effect types ---
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        # --- STATIC TAB ---
        vBoxStatic = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.staticColorButton = Gtk.ColorButton()
        vBoxStatic.pack_start(self.staticColorButton, True, True, 0) # Use pack_start for consistency
        self.stack.add_titled(vBoxStatic, "static", "Static")

        # --- CYCLE TAB ---
        vBoxCycle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.adjCycle = Gtk.Adjustment(value=5000, lower=500, upper=65535, step_increment=100, page_increment=1000, page_size=0)
        self.sbCycle = Gtk.SpinButton()
        self.sbCycle.set_adjustment(self.adjCycle)
        self.sbCycle.set_numeric(True)
        vBoxCycle.pack_start(Gtk.Label(label="Speed (500-65535ms):"), False, False, 0)
        vBoxCycle.pack_start(self.sbCycle, False, False, 0)
        self.stack.add_titled(vBoxCycle, "cycle", "Cycle")

        # --- BREATHE TAB ---
        vBoxBreathe = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.breatheColorButton = Gtk.ColorButton()
        self.adjBCycle = Gtk.Adjustment(value=5000, lower=500, upper=65535, step_increment=100, page_increment=1000, page_size=0)
        self.sbBCycle = Gtk.SpinButton()
        self.sbBCycle.set_adjustment(self.adjBCycle)
        self.sbBCycle.set_numeric(True)
        vBoxBreathe.pack_start(Gtk.Label(label="Color:"), False, False, 0)
        vBoxBreathe.pack_start(self.breatheColorButton, False, False, 0)
        vBoxBreathe.pack_start(Gtk.Label(label="Speed (500-65535ms):"), False, False, 0)
        vBoxBreathe.pack_start(self.sbBCycle, False, False, 0)
        self.stack.add_titled(vBoxBreathe, "breathe", "Breathe")

        # --- SEGMENTS TAB (G213 specific ideally) ---
        hBoxSegments = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5) # Use HORIZONTAL
        self.segmentColorBtns = [Gtk.ColorButton() for _ in range(5)]
        for i, btn in enumerate(self.segmentColorBtns):
            segment_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            segment_label_box.pack_start(Gtk.Label(label=f"Seg {i+1}"), False, False, 0)
            segment_label_box.pack_start(btn, True, True, 0)
            hBoxSegments.pack_start(segment_label_box, True, True, 0)
        self.stack.add_titled(hBoxSegments, "segments", "Segments (G213)")

        # --- Stack Switcher and Stack addition to main VBox ---
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        vBoxMain.pack_start(self.stack_switcher, False, False, 0) # Don't expand switcher
        vBoxMain.pack_start(self.stack, True, True, 0)

        # --- SET Buttons per product ---
        hBoxSetButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        for p in PRODUCTS:
            btn = Gtk.Button.new_with_label(f"Set {p}")
            btn.connect("clicked", self.on_button_clicked, p)
            hBoxSetButtons.pack_start(btn, True, True, 0)
        vBoxMain.pack_start(hBoxSetButtons, False, False, 5) # Add some margin

        # --- SET ALL Button ---
        btnSetAll = Gtk.Button.new_with_label("Set all Products")
        btnSetAll.connect("clicked", self.on_button_clicked, "all")
        vBoxMain.pack_start(btnSetAll, False, False, 0)
        
        # --- Autostart Checkboxes Section ---
        vBoxMain.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin_top=10, margin_bottom=5), False, False, 0)
        autostart_label = Gtk.Label(label="<b>Apply user settings on login:</b>", use_markup=True, xalign=0)
        vBoxMain.pack_start(autostart_label, False, False, 0)
        
        hBoxAutostartChecks = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
        self.autostart_checkboxes = {}
        for product in PRODUCTS:
            checkbox = Gtk.CheckButton(label=f"{product}")
            checkbox.connect("toggled", self.on_autostart_toggled, product)
            desktop_file_path = self._get_autostart_desktop_file_path(product)
            if os.path.exists(desktop_file_path):
                checkbox.set_active(True)
            self.autostart_checkboxes[product] = checkbox
            hBoxAutostartChecks.pack_start(checkbox, False, False, 0)
        vBoxMain.pack_start(hBoxAutostartChecks, False, False, 5)


    def btnGetHex(self, btn):
        color = btn.get_rgba()
        red = int(color.red * 255)
        green = int(color.green * 255)
        blue = int(color.blue * 255)
        hexColor = f"{red:02x}{green:02x}{blue:02x}"
        return hexColor

    def sbGetValue(self, sb):
        return sb.get_value_as_int()

    def _get_user_config_path(self, product_name):
        return os.path.join(USER_CONFIG_DIR, f"{product_name}.conf")

    def _get_autostart_desktop_file_path(self, product_name):
        return os.path.join(self.autostart_dir, f"g213colors-autostart-{product_name}.desktop")

    def _show_error_dialog(self, primary_text, secondary_text=""):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=primary_text,
        )
        if secondary_text:
            dialog.format_secondary_text(secondary_text)
        dialog.run()
        dialog.destroy()

    def on_autostart_toggled(self, checkbox, product_name):
        desktop_file_path = self._get_autostart_desktop_file_path(product_name)
        if checkbox.get_active():
            desktop_content = f"""[Desktop Entry]
Name=G213Colors Autostart ({product_name})
Comment=Apply saved G213Colors settings for {product_name} on login
Exec=/usr/bin/g213colors-gui --apply-user-config {product_name}
Icon=g213colors
Terminal=false
Type=Application
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""
            try:
                with open(desktop_file_path, "w") as f:
                    f.write(desktop_content)
                os.chmod(desktop_file_path, 0o775) # rwxrwxr-x
                logger.info(f"Created autostart entry for {product_name} at {desktop_file_path}")
            except IOError as e:
                logger.error(f"Failed to create autostart file for {product_name}: {e}")
                self._show_error_dialog(f"Error creating autostart for {product_name}", str(e))
                checkbox.set_active(False)
        else:
            if os.path.exists(desktop_file_path):
                try:
                    os.remove(desktop_file_path)
                    logger.info(f"Removed autostart entry for {product_name} from {desktop_file_path}")
                except OSError as e:
                    logger.error(f"Failed to remove autostart file for {product_name}: {e}")
                    self._show_error_dialog(f"Error removing autostart for {product_name}", str(e))
                    checkbox.set_active(True)

    def sendStatic(self, product):
        logger.info(f"Initiating static color for {product}")
        controller = G213Colors.LogitechDevice(product)
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            self._show_error_dialog(f"Connection failed: {product}", "Could not connect to the device. Check USB connection and permissions (udev rules).")
            return

        color_hex = self.btnGetHex(self.staticColorButton)
        if controller.send_color_command(color_hex):
            logger.info(f"Static color command sent to {product}.")
            field_for_static = 0 
            command_to_save = controller.spec["colorCommand"].format(f"{field_for_static:02x}", color_hex)
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(command_to_save, user_conf_path)
        else:
            logger.error(f"Failed to send static color command to {product}.")
            self._show_error_dialog(f"Command Failed: {product}", "Could not send static color command.")
        controller.disconnect()

    def sendBreathe(self, product):
        logger.info(f"Initiating breathe effect for {product}")
        controller = G213Colors.LogitechDevice(product)
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            self._show_error_dialog(f"Connection failed: {product}", "Could not connect to the device.")
            return

        color_hex = self.btnGetHex(self.breatheColorButton)
        speed = self.sbGetValue(self.sbBCycle)
        if controller.send_breathe_command(color_hex, speed):
            logger.info(f"Breathe command sent to {product}.")
            command_to_save = controller.spec["breatheCommand"].format(color_hex, f"{speed:04x}")
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(command_to_save, user_conf_path)
        else:
            logger.error(f"Failed to send breathe command to {product}.")
            self._show_error_dialog(f"Command Failed: {product}", "Could not send breathe command.")
        controller.disconnect()

    def sendCycle(self, product):
        logger.info(f"Initiating cycle effect for {product}")
        controller = G213Colors.LogitechDevice(product)
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            self._show_error_dialog(f"Connection failed: {product}", "Could not connect to the device.")
            return

        speed = self.sbGetValue(self.sbCycle)
        if controller.send_cycle_command(speed):
            logger.info(f"Cycle command sent to {product}.")
            command_to_save = controller.spec["cycleCommand"].format(f"{speed:04x}")
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(command_to_save, user_conf_path)
        else:
            logger.error(f"Failed to send cycle command to {product}.")
            self._show_error_dialog(f"Command Failed: {product}", "Could not send cycle command.")
        controller.disconnect()

    def sendSegments(self, product):
        logger.info(f"Initiating segment colors for {product}")
        if product == "G203": # G203 doesn't support segments, treat as full static color
            logger.warning("Segment mode is not applicable to G203. Applying color from first segment to whole device.")
            # Use color from first segment button for the whole device
            # Or disable this option if G203 is selected for segments in GUI
            self.staticColorButton.set_rgba(self.segmentColorBtns[0].get_rgba()) # Set static color button
            self.sendStatic(product) # Send as a static command
            return

        controller = G213Colors.LogitechDevice(product)
        if not controller.connect():
            logger.error(f"Failed to connect to {product}. Aborting command.")
            self._show_error_dialog(f"Connection failed: {product}", "Could not connect to the device.")
            return

        commands_to_save_list = []
        all_segments_sent_successfully = True
        for i in range(1, 6): 
            segment_color_hex = self.btnGetHex(self.segmentColorBtns[i-1])
            logger.debug(f"Sending segment {i} color {segment_color_hex} for {product}")
            if not controller.send_color_command(segment_color_hex, i):
                logger.error(f"Failed to send color for segment {i} to {product}.")
                all_segments_sent_successfully = False
                break 
            
            command_for_segment = controller.spec["colorCommand"].format(f"{i:02x}", segment_color_hex)
            commands_to_save_list.append(command_for_segment)
            sleep(0.01) 
        
        if all_segments_sent_successfully:
            logger.info(f"All segment commands sent to {product}.")
            full_data_to_save = "\n".join(commands_to_save_list)
            user_conf_path = self._get_user_config_path(product)
            controller.save_configuration(full_data_to_save, user_conf_path)
        else:
            logger.warning(f"Segment color setting partially failed for {product}. Configuration not saved for this attempt.")
            self._show_error_dialog(f"Segment Command Failed: {product}", "Could not send all segment color commands.")
        controller.disconnect()

    def sendManager(self, product_target):
        if product_target == "all":
            logger.info("Applying current effect settings to all configured products.")
            for p in PRODUCTS:
                self.sendManager(p) 
        else:
            self.stackName = self.stack.get_visible_child_name()
            logger.info(f"Managing '{self.stackName}' settings for product: {product_target}")
            if self.stackName == "static":
                self.sendStatic(product_target)
            elif self.stackName == "cycle":
                self.sendCycle(product_target)
            elif self.stackName == "breathe":
                self.sendBreathe(product_target)
            elif self.stackName == "segments":
                self.sendSegments(product_target)

    def on_button_clicked(self, button, product):
        logger.debug(f"Set button clicked for product: {product}. Current effect tab: {self.stack.get_visible_child_name()}")
        self.sendManager(product)

# --- Main Execution Guard ---
if __name__ == "__main__":
    # The argparse logic at the top of the file handles CLI arguments and exits if they are processed.
    # If the script reaches here, it means no CLI action arguments (-t or -auc) were specified and processed to exit.
    # Therefore, launch the GUI.
    
    logger.info("No specific CLI action requested by args, launching G213Colors GUI.")
    try:
        win = Window()
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except Exception as e:
        logger.critical(f"Critical error launching GUI: {e}", exc_info=True)
        # Fallback to console message if Gtk can't show error or before Gtk is fully up
        print(f"CRITICAL GUI LAUNCH ERROR: {e}", file=sys.stderr)
        # Attempt to show a Gtk error dialog if Gtk is somewhat functional
        try:
            error_dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Fatal Error Launching G213Colors",
            )
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
        except Exception as ed_e:
            print(f"Could not display Gtk error dialog: {ed_e}", file=sys.stderr)
        sys.exit(1)
