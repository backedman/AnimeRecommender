import pathlib
import sys
import configparser


class Config(object):
    """Handles configuration file related operations"""

    def __init__(self) -> None:
        """Initializes the Config object and reads or creates the config file"""
        
        self.configObj = configparser.ConfigParser()

        # Check if the config file exists
        confExists = pathlib.Path("config.ini").exists()
        if confExists:
            try:
                # Read the existing config file
                self.configObj.read("config.ini")
            except Exception as e:
                print(f"Error reading config file: {e}", file=sys.stderr)
        else:
            try:
                # Create a new config file with default settings
                self.configObj.add_section('user_info')
                self.configObj.set('user_info', 'username', "")
                self.configObj.add_section('settings')
                self.configObj.set('settings', 'do not show', "")
                self.configObj.set('settings', 'weighting', 'None')
                self.configObj.set('settings', 'weighting_strength', 'linear')

                # Write the new config file
                with open("config.ini", 'w+') as file:
                    self.configObj.write(file)
            except Exception as e:
                print(f"Error creating config file: {e}", file=sys.stderr)

    def get_config(self):
        """Returns the configuration object"""
        return self.configObj

    def rewrite_config(self, configObj):
        """Updates the config and writes it to the config file
        
        Arguments:
            configObj: The configuration object to be written
        """
        try:
            with open("config.ini", 'w+') as file:
                configObj.write(file)
            self.configObj = configObj
        except Exception as e:
            print(f"Error writing config file: {e}", file=sys.stderr)
