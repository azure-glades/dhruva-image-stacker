# Image stacker
- Simple image stacker program that takes 7 fits files as an input
- Opens up a web-app that lets you upload .fits files. Files are stacked and the image is displayed on the web-page
- Remember to add the files in order of increasing filter wavelength
- Multi-dimensional fits data is converted to standard 3 channel image via weighted mean stacking (which is why it is important to add files in order)
- See required libraries in dependencies.txt

### Features planned
- Setting to choose lupton stacking algorithm
- Flexibility in number of fits files
- Choosing the weighted-mean of fits files
