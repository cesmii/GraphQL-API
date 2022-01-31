### Get Started
- In frontend/src/index.js: Change line 18-32 accordingly
- Install NodeJS **LTS** version from <a href="https://nodejs.org/en/?ref=creativetim">NodeJs Official Page</a>
- Download the product on this page
- Unzip the downloaded file to a folder in your computer
- Open Terminal
- Go to your file project (where you’ve unzipped the product)
- (If you are on a linux based terminal) Simply run `npm run install:clean`
- (If not) Run in terminal `npm install apexcharts --save`     
- (If not) Run in terminal `npm install react-apexcharts apexcharts`
- (If not) Run in terminal `npm install`
- (If not) Run in terminal `npm run build:tailwind` (do not run this at the first time. each time you add a new class, a class that does not exist in `src/assets/styles/tailwind.css`, you will need to run this command)
- (If not) Run in terminal `npm start`
- Navigate to https://localhost:3000


### Run with simulation
- 1. run `python3 gateway.py -m multitanks` in one terminal
- 2. - for multitank model: run `python3 simulate.py tank normalflow` in another terminal
     - for onetank model: run `python3 simulate.py tank fillthendrain` in another terminal
- 3. check on the gateway terminal -> after you get all the responses of the first sierie of queries -> go on the animation page -> refresh -> click on multitanks tab on the left