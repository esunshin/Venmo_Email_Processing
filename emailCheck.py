import time
from itertools import chain
import email
import imaplib
import html

import data.emailCheckData as user
import dataSender

imap_ssl_host = user.host
imap_ssl_port = user.port
username = user.name
password = user.password

# Restrict mail search. Be very specific.
# Machine should be very selective to receive messages.
#criteria = {
#    'FROM':    'venmo@venmo.com',
#    'SUBJECT': 'SPECIAL SUBJECT LINE',
#    'BODY':    'SECRET SIGNATURE',
#}
criteria = {
    'FROM':    'venmo@venmo.com',
}
uid_max = 0


def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    print('(%s)' % ' '.join(chain(*c)))
    return '(%s)' % ' '.join(chain(*c))
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)


def get_first_text_block(msg):
    type = msg.get_content_maintype()

    if type == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif type == 'text':
        return msg.get_payload()


server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
server.login(username, password)
resp = server.select('INBOX')
print(resp)


typ, msgnums = server.search(None, '(FROM "venmo@venmo.com" SUBJECT "paid you" NOT X-GM-LABELS venmo_processed)')

msgnums = msgnums[0].decode("utf-8")
msgnums = ''.join(msgnums)
nums = msgnums.split(" ")
#print(nums)

for num in nums:
    print(num)
    t, data = server.fetch(num, '(RFC822)')
    assert t == 'OK'
    subject = data[0][1].decode("utf-8").split("Subject: ")[1].split("\n")[0]
    sender, amount = subject.split(" paid you $")
    note = data[0][1].decode("utf-8").split("<!-- note -->")[1].split("<p>")[1].split("</p>")[0]
    print(sender)
    print(amount)
    note = html.unescape(note)
    if "=" in note:
        note = note.replace('=\r\n', '')
        note = note.replace('=','\\x')
        note = note.encode()
        note = note.decode('unicode-escape').encode('latin1').decode('utf8')
        print(note)
    else:
        print(note)
    note = "🍪107"
    if "🍪" not in note:
        continue
    else:
        print("Sending data...")
        dataSender.sendData(sender, amount, note)
        result = server.store(num, '+X-GM-LABELS', 'venmo_processed')
        assert result[0] == 'OK'
exit()

