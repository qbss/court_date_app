import paramiko
import email
import csv
from helpers import base


# dummy function to test testing
def pt_dummy(z):
    return z+1


def read_auth():
    """
    Inputs authorization info from external file.
    :return: four element tuple
    """

    with open(base('priv', 'paramikossh.txt')) as auth:
        auth_reader = csv.DictReader(auth)
        for row in auth_reader:
            if row['Variable'] == 'url':
                url = row['Value']
            elif row['Variable'] == 'account_id':
                account_id = row['Value']
            elif row['Variable'] == 'keyfile':
                keyfile = row['Value']
            else:
                passwd = row['Value']
    return url, account_id, passwd, keyfile

if __name__ == '__main__':

    url, account_id, passwd, keyfile = read_auth()
    print 'url, account_id, passwd, keyfile  =', url, account_id  #, passwd, keyfile

    # http://stackoverflow.com/questions/9963391/how-do-use-paramiko-rsakey-from-private-key
    client = paramiko.SSHClient()
    bhkey = paramiko.RSAKey.from_private_key_file(keyfile)
    # http://jessenoller.com/blog/2009/02/05/ssh-programming-with-paramiko-completely-different
    # Don't do "missing_host_key" on linux, and maybe figure out how to do known hosts on Windows.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(url, username=account_id, password=passwd, pkey=bhkey)

    # http://stackoverflow.com/questions/30626615/how-to-downlad-only-the-latest-file-from-sftp-server-with-paramiko
    sftp = client.open_sftp()
    sftp.chdir('mail/whenismycourtdate.com/data/cur/')

    latest = 0
    latestfile = None

    for fileattr in sftp.listdir_attr():
        #print fileattr
        if fileattr.st_mtime > latest:
            latest = fileattr.st_mtime
            latestfile = fileattr.filename

    if latestfile is not None:
        print
        print 'File to get = ', latestfile
        print
        sftp.get(latestfile, base('priv','email_file.txt'))
    client.close()

    msg = email.message_from_file(open(base('priv','email_file.txt')))
    #print "msg = ", msg
    print "len = ", len(msg.get_payload())
    attachment = msg.get_payload()[2]
    print attachment.get_content_type()

    #open('..\\data\\odyssey\odyssey.txt', 'wb').write(attachment.get_payload(decode=True))
    open(base('..', 'data', 'odyssey', 'odyssey.txt'), 'wb').write(attachment.get_payload(decode=True))
