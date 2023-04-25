from configparser import ConfigParser


def db_config(filename='config.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def api_config(filename='config.ini', section='API'):
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    if parser.has_section(section):
        params = parser.items(section)
        api_token = params[0][1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return api_token


def domain_config(filename='config.ini', section='domain'):
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    if parser.has_section(section):
        params = parser.items(section)
        host, port = params[0][1], params[0][2]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return host, port
