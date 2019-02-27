"""
all the methods relating to the connection established with git server
"""

import urllib

def extract_lines(data):
    """
    extract lines from data
    
    extract list of lines from given server data
    
    :param data: server data
    :type data: hex string
    :return: lines from data
    :rtype: list
    """

    lines = []
    i = 0
    for _ in range(1000):
        line_length = int(data[i:i+4], base=16)
        line = data[i+4:i+line_length]
        lines.append(line)
        if line_length == 0:
            i+=4
        else:
            i += line_length
        if i >= len(data):
            break
    return lines

def build_lines_data(lines):
    """
    build byte string for lines
    
    build byte string from given lines to send to server
    
    :param lines: lines of data
    :type lines: list
    :return: [description]
    :rtype: [type]
    """

    result = []
    for line in lines:
        result.append('{:04x}'.format(len(line)+5).encode())
        result.append(line)
        result.append(b'\n')
    result.append(b'0000')
    return result

def http_request(url, username, password, data=None):
    """
    make http GET/POST request
    
    make an authenticated HTTP request to given url
    makes a POST request when data is not None, GET otherwise
    
    :param url: url of the website 
    :type url: string
    :param username: git client username
    :type username: string
    :param password: git client password
    :type password: string
    :param data: data to be sent in POST request, defaults to None
    :param data: byte string, optional
    :return: response of the website
    :rtype: JSON
    """

    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, username, password)
    auth_handler = urllib.request.HTTPDigestAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_handler)
    f = opener.open(url, data=data)
    return f.read()

def get_remote_master_branch(git_url, username, password):
    """
    get master branch information from remote
    
    get commit hash of remote master branch, return SHA-1 hex string or None is no remote commits
    
    :param git_url: repository URL
    :type git_url: string
    :param username: git client username
    :type username: string
    :param password: git client password
    :type password: string
    :return: remote master branch commit
    :rtype: string
    """

    url = git_url + '/info/refs?service=git-receive-pack'
    response = http_request(url, username, password)
    lines = extract_lines(response)
    assert lines[0] == b'# service=git-receive-pack\n'
    assert lines[1] == b''
    if lines[2][:40] == b'0' * 40:
        return None
    master_sha1, master_ref = lines[2].split(b'\x00')[0].split()
    assert master_ref == b'refs/heads/master'
    assert len(master_sha1) == 40
    return master_sha1.decode()