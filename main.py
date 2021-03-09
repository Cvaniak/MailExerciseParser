from imap_tools import MailBox, AND
from tinydb import TinyDB, Query
from optparse import OptionParser, OptionValueError
import webbrowser
import datetime
import getpass
import os
import sys
from dotenv import load_dotenv
load_dotenv()

DEFAULT_HOST = "imap.gmail.com"
ALLOW_LESSSECURE = "https://myaccount.google.com/lesssecureapps"

class Declaration:
	declared_ex = None
	def __init__(self, mailObject):
		self.subject = mailObject.subject
		self.uid = mailObject.uid
		self.name = mailObject.from_values["name"]
		self.date = mailObject.date


	def parse_subject(self):
		try:
			self.declared_ex = list(map(int, "".join(self.subject.split()).split(",")))
			ch = self.check_declared_ex()
			self.declared_ex = list(set(self.declared_ex))
			self.declared_ex.sort()
			return ch
		except:
			return 1

	def check_declared_ex(self):
		try:
			ch1 = not all(isinstance(x,int) for x in self.declared_ex) or not self.declared_ex
			return ch1
		except:
			return 1

	def __str__(self):
		return (f"uID = {self.uid}\n"
			f"Name = {self.name}\n"
			f"Date = {self.date}\n"
			f"Subject = {self.subject}\n"
			f"List = {self.declared_ex or 'Not parsed or empty'}\n")


def create_dotenv(option, opt, value, parser):
	last_host = os.getenv("HOST") if os.getenv("HOST") else DEFAULT_HOST
	host_name = input(f"HOST = ({last_host})") or last_host
	last_mail = f"({os.getenv('MAIL')}) or type new -> " if os.getenv('MAIL') else ""
	mail = input(f"Your mail = {last_mail}") or os.getenv("MAIL")
	if os.getenv("PASSWORD"):
		pass_mes = "(leave last password) or type new *HIDDEN*"
	else:
		pass_mes = "(leave empty) or type new password *HIDDEN*"
	password = getpass.getpass((f"Your password = {pass_mes}")) or os.getenv("PASSWORD")
	f = open(".env", "w")
	f.write(f"HOST='{host_name}'\n")
	f.write(f"MAIL='{mail}'\n")
	f.write(f"PASSWORD='{password}'\n")
	f.close()
	load_dotenv()


def get_mails(options):
	host = os.getenv("HOST") or DEFAULT_HOST
	login = os.getenv("MAIL") or input("Type your mail address: ")
	password = os.getenv("PASSWORD") or getpass.getpass("Type password *HIDDEN*")
	with MailBox(os.getenv("HOST")).login(os.getenv("MAIL"), password) as mailbox:
	    msg = mailbox.fetch(AND(date_gte=options.date_from.date(), date_lt=options.date_to.date()))
	    for i in msg:
	    	dec = Declaration(i)
	    	if not dec.parse_subject():
	    		mail_list.append(dec)
	    		print(mail_list[-1])


def open_lesssecure(option, opt, value, parser):
	webbrowser.open(ALLOW_LESSSECURE)


def date_callback(option, opt, value, parser):
	print(f"{option}, {opt}, {value}, {parser}")
	try:	
		setattr(parser.values, option.dest, datetime.datetime.strptime(value,'%d.%m.%Y'))
	except Exception as e:
		raise OptionValueError(f"Wrong date format {e}")


def parse_options():
	parser = OptionParser()
	parser.add_option("-s", "--lesssecure",
					  action="callback",
					  help=f"Opens browser on {ALLOW_LESSSECURE} to enable lesssecureapps on gmail",
					  callback=open_lesssecure)
	parser.add_option("-e", "--env",
					  action="callback", 
					  help="Setup host, mail and password in .env", callback=create_dotenv)
	parser.add_option("-f", "--date_from",
	                  action="callback", type="string",
	                  help="Newer mails than this date will be checked", callback=date_callback)
	parser.add_option("-t", "--date_to",
	                  action="callback", type="string",
	                  help="Older mails than this date will be chcked", callback=date_callback)

	return parser


if __name__ == "__main__":
	(options, args) = parse_options().parse_args()
	# db = TinyDB('db.json')
	print(f"{options}, {args}")
	required = ["date_to", "date_from"]
	for r in required:
	    if options.__dict__[r] is None:
	        print(f"Parameter {r} is required")	
	        sys.exit()
	mail_list = []
	get_mails(options)