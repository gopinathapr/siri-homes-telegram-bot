#virtualenv venv
source venv/bin/activate
pip3 install flask
pip3 install python-telegram-bot
python3 enquiry-bot.py &
python3 writer-bot.py &
python3 web.py