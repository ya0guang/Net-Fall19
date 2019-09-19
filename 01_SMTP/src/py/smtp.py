#!/usr/bin/env python3

import os
import time
import smtplib
import argparse

# Entry function for sending mail via SMTP.  The input arguments allow you to
# construct a well-formed email message and send it a specific server.

def send_mail(server, faddr, taddr, msg):
    print (server, faddr, taddr, msg)

    host = server
    port = 25
    smtpObj = smtplib.SMTP(host, port)

    msg = ("From: %s\r\nSubject: Ghost Msg\r\nTo: %s\r\n\r\n %s") % (faddr, taddr, msg)

    smtpObj.set_debuglevel(3)

    try:
        smtpObj.sendmail(faddr, taddr, msg)
    except Exception as e:
        print(e)

    smtpObj.quit()

    #print(msg)



def main():
    parser = argparse.ArgumentParser(description="SICE Network SMTP Client")
    parser.add_argument('mail_server', type=str,
                        help='Server hostname or IP')
    parser.add_argument('from_address', type=str,
                        help='My email address')
    parser.add_argument('to_address', type=str,
                        help='Receiver address')
    parser.add_argument('message', type=str,
                        help='Message text to send')
    
    args = parser.parse_args()
    
    send_mail(args.mail_server, args.from_address,
              args.to_address, args.message)
    
if __name__ == "__main__":
    main()
    
