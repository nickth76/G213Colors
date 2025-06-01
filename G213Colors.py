'''
  *  The MIT License (MIT)
  *
  *  G213Colors v0.1 Copyright (c) 2016 SebiTimeWaster
  *
  *  Permission is hereby granted, free of charge, to any person obtaining a copy
  *  of this software and associated documentation files (the "Software"), to deal
  *  in the Software without restriction, including without limitation the rights
  *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  *  copies of the Software, and to permit persons to whom the Software is
  *  furnished to do so, subject to the following conditions:
  *
  *  The above copyright notice and this permission notice shall be included in all
  *  copies or substantial portions of the Software.
  *
  *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  *  SOFTWARE.
'''

import usb.core
import usb.util
import binascii
import logging
import time # Added for sleep in apply_config_from_file
import os # Added for path operations if needed within the class, though main.py will handle user paths

logger = logging.getLogger(__name__)

class LogitechDevice:
    ID_VENDOR = 0x046d
    USB_BM_REQUEST_TYPE = 0x21
    USB_BM_REQUEST = 0x09
    USB_W_INDEX = 0x0001

    PRODUCT_SPECS = {
        "G213": {
            "idProduct": 0xc336, "wValue": 0x0211,
            "colorCommand": "11ff0c3a{}01{}0200000000000000000000",
            "breatheCommand": "11ff0c3a0002{}{}006400000000000000",
            "cycleCommand": "11ff0c3a0003ffffff0000{}64000000000000",
            "needs_receive_after_color": True
        },
        "G203": {
            "idProduct": 0xc084, "wValue": 0x0210,
            "colorCommand": "11ff0e3c{}01{}0200000000000000000000",
            "breatheCommand": "11ff0e3c0003{}{}006400000000000000",
            "cycleCommand": "11ff0e3c00020000000000{}64000000000000",
            "needs_receive_after_color": False
        }
    }
    
    # System-wide default config file (for -t option)
    SYSTEM_DEFAULT_CONF_FILE = "/etc/G213Colors.conf"


    def __init__(self, product_name):
        if product_name not in self.PRODUCT_SPECS:
            raise ValueError(f"Unsupported product: {product_name}")
        self.product_name = product_name
        self.spec = self.PRODUCT_SPECS[product_name]
        self.device = None
        self.is_kernel_driver_detached = False
        logger.debug(f"LogitechDevice instance created for {self.product_name}")

    # ... (connect, disconnect, _send_data, _receive_data methods remain the same as previously proposed) ...
    def connect(self):
        logger.info(f"Attempting to connect to: {self.product_name}")
        try:
            self.device = usb.core.find(idVendor=self.ID_VENDOR, idProduct=self.spec["idProduct"])
            if self.device is None:
                logger.error(f"USB device {self.product_name} not found!")
                return False

            if self.device.is_kernel_driver_active(self.USB_W_INDEX):
                self.device.detach_kernel_driver(self.USB_W_INDEX)
                self.is_kernel_driver_detached = True
            logger.info(f"Connected to {self.product_name}")
            return True
        except usb.core.USBError as e:
            logger.error(f"USBError during connect for {self.product_name}: {e}")
            if "access" in str(e).lower() or "permission" in str(e).lower():
                logger.error("This might be a permissions issue. Ensure udev rules are set or run with sufficient privileges if not using the GUI's Polkit method.")
            self.device = None
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connect for {self.product_name}: {e}")
            self.device = None
            return False

    def disconnect(self):
        if not self.device:
            # logger.warning(f"Disconnect called for {self.product_name}, but no device was connected or connection failed.")
            return # It's okay if disconnect is called without active device

        logger.info(f"Disconnecting from {self.product_name}")
        try:
            usb.util.dispose_resources(self.device)
            if self.is_kernel_driver_detached:
                # Re-finding explicitly to attach is safer if device handle got invalidated by dispose.
                # However, attach_kernel_driver is a method of the device object itself.
                # For robustness, let's try to re-find, but have a fallback.
                try:
                    temp_device_for_attach = usb.core.find(idVendor=self.ID_VENDOR, idProduct=self.spec["idProduct"])
                    if temp_device_for_attach:
                        logger.info(f"Reattaching kernel driver for {self.product_name} (using re-found device instance)")
                        temp_device_for_attach.attach_kernel_driver(self.USB_W_INDEX)
                    else: # Fallback if not re-found (e.g. device unplugged right after dispose)
                         logger.warning(f"Could not re-find {self.product_name} to reattach kernel driver. Attempting with stored device handle.")
                         self.device.attach_kernel_driver(self.USB_W_INDEX) # Try with original handle
                except usb.core.USBError as attach_err:
                     logger.error(f"USBError reattaching kernel driver (re-find attempt) for {self.product_name}: {attach_err}")
                self.is_kernel_driver_detached = False
        except usb.core.USBError as e:
            logger.error(f"USBError during disconnect/reattach for {self.product_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during disconnect for {self.product_name}: {e}")
        finally:
            self.device = None

    def _send_data(self, data_hex_string):
        if not self.device:
            logger.error(f"Cannot send data to {self.product_name}, device not connected.")
            return False
        logger.debug(f"Sending data to {self.product_name}: {data_hex_string}")
        try:
            self.device.ctrl_transfer(
                self.USB_BM_REQUEST_TYPE, self.USB_BM_REQUEST,
                self.spec["wValue"], self.USB_W_INDEX,
                binascii.unhexlify(data_hex_string)
            )
            return True
        except usb.core.USBError as e:
            logger.error(f"USBError sending data to {self.product_name}: {e}")
            return False

    def _receive_data(self):
        if not self.device:
            logger.error(f"Cannot receive data from {self.product_name}, device not connected.")
            return None
        try:
            data = self.device.read(0x82, 64, timeout=100) 
            logger.debug(f"Received data from {self.product_name}: {binascii.hexlify(data)}")
            return data
        except usb.core.USBError as e:
            if e.errno == 110:
                 logger.debug(f"Read from {self.product_name} timed out, this might be normal.")
                 return None
            logger.error(f"USBError receiving data from {self.product_name}: {e}")
            return None

    def send_color_command(self, color_hex, field=0):
        command_string = self.spec["colorCommand"].format(str(format(field, '02x')), color_hex)
        if self._send_data(command_string):
            if self.spec["needs_receive_after_color"]:
                self._receive_data()
            return True
        return False

    def send_breathe_command(self, color_hex, speed):
        command_string = self.spec["breatheCommand"].format(color_hex, str(format(speed, '04x')))
        return self._send_data(command_string)

    def send_cycle_command(self, speed):
        command_string = self.spec["cycleCommand"].format(str(format(speed, '04x')))
        return self._send_data(command_string)

    def save_configuration(self, command_data_string, file_path):
        """Saves the product name and provided command string(s) to the specified file path."""
        logger.info(f"Saving configuration for {self.product_name} to {file_path}")
        # command_data_string can be a single command or multiple commands separated by newlines
        try:
            # Ensure directory exists (useful for user-specific paths)
            dir_name = os.path.dirname(file_path)
            if dir_name: # Check if dir_name is not empty (e.g. for relative paths in current dir)
                 os.makedirs(dir_name, exist_ok=True)

            with open(file_path, "w") as f:
                f.write(f"PRODUCT={self.product_name}\n") # Save product name first
                f.write(command_data_string) # Save the command(s)
            logger.info(f"Configuration saved successfully to {file_path}.")
            return True
        except (IOError, OSError, PermissionError) as e: # Catch OSError for makedirs
            logger.error(f"Failed to save configuration to {file_path}: {e}")
            if isinstance(e, PermissionError):
                logger.error("This is a permission error. Ensure the application has rights to write to this file.")
            return False

    @classmethod
    def apply_configuration_from_file(cls, conf_file_path):
        """Loads configuration from a file, determines product, and applies settings."""
        logger.info(f"Attempting to apply settings from configuration file: {conf_file_path}")
        try:
            with open(conf_file_path, "r") as file:
                first_line = file.readline().strip()
                if not first_line.startswith("PRODUCT="):
                    logger.error(f"Invalid config file format in {conf_file_path}. Missing PRODUCT line.")
                    return False
                
                product_name_from_file = first_line.split("=", 1)[1]
                logger.info(f"Product identified in config file: {product_name_from_file}")

                commands_to_apply = [line.strip() for line in file if line.strip()]

            if not commands_to_apply:
                logger.warning(f"No commands found in {conf_file_path} for product {product_name_from_file}.")
                return True # No commands to apply, but not an error per se

            device_instance = cls(product_name_from_file) # Create instance of the correct product
            
            if not device_instance.connect():
                logger.error(f"Could not connect to {product_name_from_file} to apply settings.")
                return False

            logger.info(f"Applying {len(commands_to_apply)} command(s) to {product_name_from_file}...")
            success = True
            for cmd_data in commands_to_apply:
                if device_instance._send_data(cmd_data):
                    if device_instance.spec["needs_receive_after_color"]:
                         device_instance._receive_data()
                    time.sleep(0.01) # Original sleep
                else:
                    logger.error(f"Failed to send command: {cmd_data} to {product_name_from_file}")
                    success = False
                    break # Stop on first error
            
            device_instance.disconnect()
            if success:
                logger.info(f"Finished applying settings from {conf_file_path} for {product_name_from_file}.")
            else:
                logger.warning(f"Settings from {conf_file_path} for {product_name_from_file} were partially applied due to errors.")
            return success

        except FileNotFoundError:
            logger.warning(f"Configuration file {conf_file_path} not found. Cannot apply settings.")
            return False # Indicate failure to apply
        except ValueError as e: # Catches unsupported product from cls(product_name_from_file)
            logger.error(f"Error processing configuration file {conf_file_path}: {e}")
            return False
        except (IOError, PermissionError) as e:
            logger.error(f"Error reading configuration file {conf_file_path}: {e}")
            return False
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error applying settings from file {conf_file_path}: {e}")
            return False
