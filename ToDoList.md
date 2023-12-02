
## Still To Do
* implement an user guide

*Job Tests* 
* test if cpep job script is running (success and fail)
* test if rsremd job script is running (success and fail)
    * rsremd job simulation takes so long, which is why it is so annyoing to run it everytime you want to make a unit test
    * idea: maybe only include fails into unit test and let the success test run seperate
* test if email successful
    * it is hard to test the mail because it starts the whole job simulation which takes so long - find a way to bypass this
* test the form validators
* test automated delete function

*Ideas*
* publish the repository onto github to use swimm documentation https://swimm.io/ - only works with GitHub
* let job sim output be wrtten into a output.file (currently the job simulation output is printed)
* embelish email to look more professional (tum icon, t38 image, etc)
* change upload file button look

## Done
* scripts are running
* emails sent with correct links
* downloading and opening result.zip works
* delete function is written and works
* unit tests implemented - apart from the above
* source control implemented with local git