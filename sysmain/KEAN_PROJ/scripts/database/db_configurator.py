"""
    db_configurator.py file
    @module: db_utils
    @author: Andrew Good & Chang Liu
    @company: Kindle Energy
    @datetime: 2017-06-13
    @version: V1.0
    this file configures the database connection info
"""

import configparser;
import sys;
import os.path;


db_config_file_path = 'db_config.ini';

def get_db_config_info(section = "DB_Production"):

    """
        get the parent path and then go for config folder to find the ini file
    """
    print ("Database mode: " + section);

    dir_path = os.path.dirname(os.path.realpath(__file__));
    parent_path = os.path.abspath(os.path.join(dir_path, os.pardir));
    parent_path = os.path.abspath(os.path.join(parent_path, os.pardir));

    global db_config_file_path;
    db_config_file_path = parent_path + '\\config\\' + db_config_file_path;

    # print (db_config_file_path);

    # sys.exit();

    config = configparser.ConfigParser()
    config.read(db_config_file_path);
    conf_dict = {};
    options = config.options(section);
    for option in options:
        try:
            conf_dict[option] = config.get(section, option);
            if conf_dict[option] == -1:
                DebugPrint("skip: %s" % option);
        except:
            print("exception on %s!" % option);
            conf_dict[option] = None;
    return conf_dict;
