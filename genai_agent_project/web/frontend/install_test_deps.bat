@echo off
echo Installing Jest and required dependencies...
npm install --save-dev jest jest-environment-jsdom @testing-library/jest-dom @testing-library/react @testing-library/user-event babel-jest @babel/preset-env @babel/preset-react @babel/plugin-transform-runtime @babel/core identity-obj-proxy jest-watch-typeahead react-app-polyfill
echo Installation complete!
pause
