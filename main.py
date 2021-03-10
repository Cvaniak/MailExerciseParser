from imap_tools import MailBox, AND
from tinydb import TinyDB, Query
from optparse import OptionParser, OptionValueError
from itertools import chain
from collections import defaultdict
import copy
import random
import webbrowser
import datetime
import getpass
import os
import sys
from dotenv import load_dotenv
load_dotenv()

DEFAULT_HOST = "imap.gmail.com"
ALLOW_LESSSECURE = "https://myaccount.google.com/lesssecureapps"


def callback_create_dotenv(option, opt, value, parser):
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


def callback_open_lesssecure(option, opt, value, parser):
	webbrowser.open(ALLOW_LESSSECURE)


def callback_date(option, opt, value, parser):
	try:	
		date_t = datetime.datetime.strptime(value,'%d.%m.%Y')
		if option.dest == "date_to":
			date_t += datetime.timedelta(days=1)
		setattr(parser.values, option.dest, date_t)	

	except Exception as e:
		raise OptionValueError(f"Wrong date format {e}")


def callback_set_manualy(option, opt, value, parser):
	try:
		setattr(parser.values, option.dest, value)
	except:
		raise OptionValueError(f"{e}")


def parse_options():
	parser = OptionParser()
	parser.add_option("-s", "--lesssecure",
					  action="callback",
					  help=f"Opens browser on {ALLOW_LESSSECURE} to enable lesssecureapps on gmail",
					  callback=callback_open_lesssecure)
	parser.add_option("-e", "--env",
					  action="callback", 
					  help="Setup host, mail and password in .env", callback=callback_create_dotenv)
	parser.add_option("-f", "--date_from",
	                  action="callback", type="string",
	                  help="Newer mails than this date will be checked", callback=callback_date)
	parser.add_option("-t", "--date_to",
	                  action="callback", type="string",
	                  help="Older mails than this date will be chcked", callback=callback_date)
	parser.add_option("-x", "--ex_from",
	                  action="store", type="int", dest="ex_from",
	                  help="The lowest index of exercise")
	parser.add_option("-y", "--ex_to",
	                  action="store", type="int", dest="ex_to",
	                  help="The highest index of exercise")
	parser.add_option("-z", "--ex_manualy",
	                  action="callback", type="string",
	                  help="Manualy set index of exercise X,Y,Z,...", callback=callback_set_manualy)
	parser.add_option("-o", "--output_file", dest="output_file",
	                  action="store", type="string",
	                  help="Output file name")
	parser.add_option("-a", "--assign_number",
	                  action="store", type="int", default=100,
	                  help="How many iteration of assign algorithm (possible failures)")

	return parser


class Declaration:
	declared_ex = None
	def __init__(self, mailObject):
		self.subject = mailObject.subject
		self.uid = mailObject.uid
		self.index = mailObject.from_values["email"].split("@")[0]
		self.name = mailObject.from_values["name"]
		self.mail = mailObject.from_values["email"]
		# self.name = mailObject.from_values['name']
		self.date = mailObject.date

	def parse_subject(self):
		try:
			self.declared_ex = list(map(int, "".join(self.subject.split()).split(",")))
			ch = self.check_declared_ex()
			self.declared_ex = set(self.declared_ex)
			# self.declared_ex.sort()
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
			f"Mail = {self.mail}\n"
			f"Name = {self.name}\n"
			f"Date = {self.date}\n"
			f"Subject = {self.subject}\n"
			f"List = {self.declared_ex or 'Not parsed or empty'}\n")


def get_mails(options):
	host = os.getenv("HOST") or DEFAULT_HOST
	login = os.getenv("MAIL") or input("Type your mail address: ")
	password = os.getenv("PASSWORD") or getpass.getpass("Type password *HIDDEN*")
	mail_list = []
	temp_name = []
	with MailBox(os.getenv("HOST")).login(os.getenv("MAIL"), password) as mailbox:
	    msg = mailbox.fetch(AND(date_gte=options.date_from.date(), date_lt=options.date_to.date()), mark_seen=False, reverse=True)
	    for i in msg:
	    	dec = Declaration(i)
	    	if not dec.parse_subject() and not (dec.mail in temp_name):
	    		mail_list.append(dec)
	    		temp_name.append(dec.mail)

	return mail_list


def assign_alg(d_list, ex_list, options):
	ex_dict = defaultdict(set)
	for ex in ex_list:
		for d in d_list:
			if ex in d.declared_ex:
				ex_dict[ex].add(d.uid)

	ex_dict_sorted = {k: v for k, v in sorted(ex_dict.items(), key=lambda x: len(x[1]))}

	keys = [k for k, v in ex_dict_sorted.items()]
	counter = options.assign_number
	while counter > 0:
		counter -= 1
		try:
			print_multi("-", end="")
			ex_temp = copy.deepcopy(ex_dict_sorted)
			end_list = []
			for i, k in enumerate(keys):
				choice = random.choice(tuple(ex_temp[k]))
				end_list.append((k, choice))

				for z in keys[:]:
					ex_temp[z].discard(choice)
			else:
				print_multi("|", end="")

			if len(end_list) == len(keys):
				print_multi("")
				break
		except:
			print_multi(f"/", end="")
			pass
	else:
		print_multi(f"Algorithm haven't found any solution")

	return end_list


def index_exercise(d_list):
	t_list = list(set(chain.from_iterable([x.declared_ex for x in d_list])))
	t_list.sort()
	return t_list


def print_multi(string_t, file_t=None, end="\n"):
	print(string_t, end="")
	print(end, end="")

	if file_t:
		with open(file_t, "a") as f:
			f.write(string_t)
			f.write(end)


def print_declarations(declaration_list):
	for i in declaration_list:
		print_multi(i)


def print_students_ex(d_list, ex_list, file_t = None):

	max_len = max([len(d.name) for d in d_list])
	c_ex = len(str(max(ex_list)))

	print_multi("", file_t)
	for ex in ex_list:
		print_multi(f"{ex:{c_ex}} |", file_t, end="")

		c = 0
		for d in d_list:
			if ex in d.declared_ex:
				print_multi(f" {d.name:{max_len}} |", file_t, end="")
				c += 1

		print_multi("", file_t)
		print_multi("-"*(c_ex+2+c*(max_len+3)), file_t)



def print_solution(d_list, solution, file_t=None):
	d_dict = {d.uid: d for d in d_list}
	max_len = max([len(d.name) for d in d_list])

	print_multi("", file_t)
	for i in solution:
		print_multi(f"{i[0]} -> {d_dict[i[1]].name:{max_len}} ({d_dict[i[1]].index})", file_t)

if __name__ == "__main__":
	# Get options
	(options, args) = parse_options().parse_args()

	# Check for required values
	required = ["date_to", "date_from"]
	for r in required:
	    if options.__dict__[r] is None:
	        print_multi(f"Parameter {r} is required")	
	        sys.exit()

	# Fetch mails
	d_list = get_mails(options)
	# Print mails
	print_declarations(d_list)

	# Choose range of exercises
	if options.ex_to and options.ex_from:
		ex_list = list([x for x in range(options.ex_from, (options.ex_to+1))])
	elif options.ex_manualy: 
		ex_list = list(map(int, options.ex_manualy.split(",")))
	else:
		ex_list = index_exercise(d_list)

	# Print students with names
	print_students_ex(d_list, ex_list, options.output_file)

	# Assign students to exercise
	solution = assign_alg(d_list, ex_list, options)
	print_solution(d_list, solution, options.output_file)