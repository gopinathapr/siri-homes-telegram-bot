from setuptools import setup, find_packages

setup(
    name='siri-homes-telegram-bot',
    version='0.1.0',
    description='A Telegram bot for Siri Homes',
    author='gopinathapr',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot>=13.0,<21.0',  # Adjust as needed
        # Add other dependencies your bot needs here
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'siri-homes-bot=your_main_module:main',  # Replace 'your_main_module' and 'main' as appropriate
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
