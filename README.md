# Setup
## To run app
With ```python3``` run:  
```bash
pip3 install requirements.txt
```  
Then you can use:  
```python
# For help
python3 main.py -h
# Simple usage 
python3 main.py --data_from DD.MM.YYYY --data_to DD.MM.YYYY
# or simpler
python3 main.py -f DD.MM.YYYY -t DD.MM.YYYY
# to setup host, mail address and optionaly password
python3 main.py -e
# to open lesssecure app in your browser
python3 main.py -s
```

## To setup Gmail (once)
First login to your Gmail account:  
![alt text](https://github.com/Cvaniak/MailExerciseParser/blob/master/images/GmailHeader.png "Step 1")  
Click here:  
![alt text](https://github.com/Cvaniak/MailExerciseParser/blob/master/images/GmailHeader_1.png "Step 2")  
And check IMAP box:  
![alt text](https://github.com/Cvaniak/MailExerciseParser/blob/master/images/GmailHeader_2.png "Step 3")  
Also go here [Google less secure apps](https://myaccount.google.com/lesssecureapps) and check this box (you can also go here from app using ```python3 main.py -s``` option:  
![alt text](https://github.com/Cvaniak/MailExerciseParser/blob/master/images/GmailHeader_3.png "Step 4")  
