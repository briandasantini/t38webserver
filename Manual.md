# Project Work Flow
*Author: Yasmin Saremi, y.saremi@tum.de*  
*Physics Department T38, Technical University of Munich, Garching, Germany*.

This project runs the website for the T38 Zacharias Group. It is implemented using Django 3.2.13 and Python 3.7.11.

My blog has links to useful websites with which this project was developed: https://ysaremi.notion.site/django-75a099a2d7574f0fbcb566ca3897a89e.

## Manual Description
This manual will assist you in understanding the project's file structure and where everything is located. It also explains how to add additional simulations to the website. Each file has its code documentation. This is simply for understanding the overall operation of the websites.

## File Structure

```
 |-- webserver/
 |    |-- contact/          <-- django app for contact page
 |    |-- jobs/             <-- django app for job simulations
 |    |    |-- migrations/
 |    |    |    +-- __init__.py
 |    |    |-- tests/       <-- contains unit tests for this app
 |    |    |    +-- some_test.py
 |    |    |-- __init__.py
 |    |    |-- admin.py
 |    |    |-- apps.py
 |    |    |-- forms.py
 |    |    |-- models.py
 |    |    |-- urls.py
 |    |    |-- validators.py
 |    |    +-- views.py
 |    |-- media/            <-- media folder
 |    |-- myproject/
 |    |    |-- __init__.py
 |    |    |-- settings.py
 |    |    |-- urls.py
 |    |    |-- wsgi.py
 |    |-- public/           <-- django app for the homepage and user guide
 |    |-- scripts/          <-- contains job simulation scripts
 |    |    |-- cpep/
 |    |    |-- rsremd/
 |    |-- static/           <-- contains images, javascript and css files 
 |    |    |-- css/
 |    |    |-- img/
 |    |    |-- js/
 |    |-- templates/        <-- contains all html files
 |    +-- manage.py
 ```

First let's start by using contact/ as an example of how the django apps are structured.
* migrations/: here Django store some files to keep track of the changes you create in the models.py file, so to keep the database and the models.py synchronized.
* tests/: this folder will contain the files that are used to write unit tests for the app.
* admin.py: this is a configuration file for a built-in Django app called Django Admin.
* apps.py: this is a configuration file of the app itself.
* forms.py: 
* models.py: here is where we define the entities of our Web application. The models are translated automatically by Django into database tables.
    * **Important**: Everytime you change something in models.py, you need to update your database
     ```bash
        python manage.py makemigrations
        python manage.py migrate
     ```
* urls.py: 
* views.py: this is the file where we handle the request/response cycle of our Web application.

Django Apps:
* contact: responsible for the contact formular
* public: responsible for the homepage, the user guide (tutorial page) and the result download page
* jobs: responsible for handling the submission of each simulation (cpep, rsremd, etc.)

The jobs application is the focal point of the entire website. It is in charge of all simulations and is the most difficult to change or add new features to. Read through *Adding New Simulations* to understand the procedure. It walks you through each stage of the process and explains how the jobs application runs collectively.

## Adding New Simulations
So you want to add new simulations to the website. <br/>
There are multiple steps to be done to add a new feauture. 
1. Make a new directory: scripts/*name of your sim*/
2. Add your script and input files into the new directory
3. Update jobs/models.py
4. Update jobs/forms.py
5. Update jobs/views.py
6. Update jobs/urls.py
7. Add HTML file
8. Update homepage and navbar dropdown menu
9. Add an user guide

I will walk you through each step - don't worry.

### New Simulation Directory with Script and Input Files
First, go to ./scripts/ and make a new directory
```
 |    |-- scripts/          
 |    |    |-- cpep/
 |    |    |-- rsremd/
 |    |    |-- newsim/                  <-- New Simulation Folder
 |    |    |    |-- script.file
 |    |    |    |-- some_input.file
 |    |    |    |-- protein_folder/     <-- Important for later, don't add this folder
 |    +-- manage.py
 ```
Place any necessary input files for the new simulation in the new simulation folder along with the script (python, bash, etc.). <br/>
A new folder on this level will be added later on during forms.py (for example, protein_folder/). <br/>
All output files must be able to be placed in the protein folder by the script file. <br/>
Every job submission is segregated in this way so that they do not conflict with one another. Make sure any input files you have may be used one level below if you have any. A script file example would be:
```bash
    cd protein_file/
    python ../some_inputfile.py
```

### Update Models
Add a new class to your jobs/models.py. Pdb, protein complex name, and email must always be included. Variables can be as many as your script requires; we'll use var 1 and 2 as examples. Adjust the variables to your needs. 
 ```python
class newsim(models.Model):
    email = models.EmailField(max_length = 254, blank=False)
    protein_complex_name = models.CharField(max_length=100, blank=False)
    var1 = models.IntegerField(blank=False, default=89)                         # This is just an example
    var2 = models.IntegerField(blank=False, default=185)                        # This is just an example
    pdb = models.FileField(null=True, blank=False, validators=[validate_file], upload_to=user_directory_path)
 ```

### Update Forms
Add a new form class into jobs/forms.py. This is the standard layout for all simulation forms. 
 ```python
 class NewSimForm(forms.ModelForm):
    class Meta:
        model = newsim
        fields = ('pdb', 'protein_complex_name', 'var1', 'var2', 'email')
        widgets = {
                'pdb': forms.FileInput(),
                'protein_complex_name': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "name"}),
                'var1': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "Variable 1"}),
                'var2': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "Variable 2"}),
                'email': forms.EmailInput(attrs={'class' : 'form-control', 'placeholder':"maxmustermann@email.de"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.use_custom_control = False
        self.helper.layout = Layout(
            'pdb',
            'protein_complex_name',
            Row(
                Column('var1', css_class='form-group col-md-6 mb-0'),
                Column('var2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            Submit('submit', 'Submit', css_class='btn btn-primary btn-block')
        )
 ```
Pdb, protein complex name, and email must always be included. Variables can be as many as your script requires; we'll use var 1 and 2 as examples. <br/>
Please define your variables' forms.  In the __init__() function, provide the widgets and how you want them displayed. It makes use of the module crispy.forms.Layout, and you may decide to show them in the same row as we did here. <br/>
Before running the script, we must first clean all provided form data:
 ```python
    def clean_data(self):
        pdb = self.cleaned_data["pdb"]
        var1 = self.cleaned_data["var1"]
        var2 = self.cleaned_data["var2"]
        reference_name1 = bleach.clean(self.cleaned_data["protein_complex_name"])
        email1 = bleach.clean(self.cleaned_data["email"])

        protein_file_name = pdb.name.replace('.pdb', '')
        reference_name = reference_name1.replace(" ","-")
        email = email1.strip()

        return protein_file_name, var1, var2, reference_name, email

    def script(self):
        # Script Specific Variable
        protein_file_name, var1, var2, reference_name, email = self.clean_data()

        simtype = 'newsim'
        file_path = './scripts/'+str(simtype)+'/'
        pdb_name = find('./media/'+protein_file_name+"/")
        cmd="python script.py "+pdb_name+" "+str(var1)+" "+str(var2)+" 2> "+pdb_name+"_errors.txt"

        # Execute Script
        exec_script(simtype, pdb_name, protein_file_name, cmd, reference_name, email)
 ```
Change the cmd variable to what suits your needs and enter the simtype, which is the name of the directory we have made before. We assumed here that the script file runs on Python and makes use of the pdb file name and variables 1 and 2. Always include the errors.txt file. This text file will be provided to the user if there is a problem during the simulation.

After that, we'll go through the exec script() function. When you alter something in this function, it impacts all simulations since they all rely on it. This is why we keep the exec_script() function outside of any class.
 ```python
    def exec_script(simtype, pdb_name, protein_file_name, cmd, reference_name, email):
        # Script Specific Names

        file_path = './scripts/'+str(simtype)+'/'
        result_folder_path = '../../media/'
        error = pdb_name+'_errors.txt'
        
        # Execute Script
        with cd(file_path):
            # Let the Specific Simulation Run
            directory = os.path.dirname(os.path.abspath(__file__))
            os.mkdir('/home/ysaremi/webserver/'+file_path+'/'+pdb_name)
            shutil.move("../../media/"+protein_file_name+"/"+pdb_name+".pdb", pdb_name+"/"+pdb_name+".pdb")
            shutil.rmtree("../../media/"+protein_file_name)
            os.system(cmd)
            shutil.move(error, pdb_name+"/"+error)

            # Figure Out The Result Condition:

            if simtype=='rsremd':
                result_condition=(os.path.exists(pdb_name+"/remd_8.pdb"))
            if simtype=='cpep':
                result_condition=(os.stat(pdb_name+'/'+error).st_size == 0)
            if simtype=='newsim':
                # Enter your result condition here! An Example:
                result_condition=(os.path.exists(pdb_name+"/result.file"))
            else:
                result_condition=False

            # Prepare Result if Successful
            if result_condition==True:
                shutil.move(pdb_name, result_folder_path+pdb_name)

        # Send Mail
        send_mail(reference_name, pdb_name, email, file_path)  
 ```
This function creates a new directory where it will save all simulation results and then executes the script command. **Please include a condition for the result.** <br/>

This could be the existence of a specific result file or the absence of content in the error file. If the result condition is True, the protein folder containing all simulation results will be relocated to the media folder and kept there for at least 30 days before being deleted automatically. <br/>

The user will then receive an email containing a unique ID that will allow them to download their result folder. If the result condition is False, the user will receive an email apologising for the unsuccessful simulation, along with the errors.txt file.

### Update Views
Add a new class to your jobs/views.py. Rename *newsim* to the actual name of the new simulation. You won't need to add anything else.
 ```python
class NewSimView(SuccessMessageMixin, FormView):
    template_name = 'newsim.html'
    model = newsim
    form_class = NewSimForm
    success_url = reverse_lazy('home')
    success_message = "Your Job has been submitted successfully"
    def form_valid(self, form):
        form.save()
        first_thread = threading.Thread(target=form.script, args=())
        # Calls the custom send_to_job method
        first_thread.start()
        return super().form_valid(form)
 ```

### Update Urls
Add a new path in jobs/urls.py. Again, rename *newsim* to the actual name for the new simulation. you won't need to add anything else.
 ```python
urlpatterns = [
    path("cpep/", cPEPView.as_view(), name="cpep"),
    path("rsremd/", RSREMDView.as_view(), name="rsremd"),
    path("newsim/", NewSimView.as_view(), name="newsim"),       # Add This Line
]
 ```

### Add HTML File
Add a new file to ./templates/
```
 |    |-- templates/ 
 |    |    |-- base.html         
 |    |    |-- cpep.html
 |    |    |-- rsremd.html
 |    |    |-- newsim.html               <-- New Simulation HTML File
 |    |    +-- 
 |    +-- manage.py
 ```
 Important: Select a simulation picture. This will be required for the Gallery on the Home Page, as well as for the simulation page.

Go to./static/img/ and place your simulation picture there.

This is the newsim.html template. Nothing more needs to be added to the html. 
 ```html
 {% extends 'base_jobs.html' %}

{% load static %}

<!--This will appear in the browser's tab.-->
{% block title %}NEWSIM{% endblock %}

<!--This will be the title of the website's header.-->
{% block header %}Name of Your Simulation{% endblock %}
<!--Add a simulation image to ./static/img/ and write the name of the img file here-->
{% block image %}{% static 'img/newsim.png' %}{% endblock %}


{% block text %}
  <p>
    Please provide a brief description of your simulation.<br>
    This text will be displayed on the website.
  </p>
{% endblock %}

<!--A named anchor is a link to a specific location on a page. The anchor name must be unique-->
{% block anchor-name %}anchor-name-for-newsim-tutorial{% endblock %}

{% block reference %}
    <a href="linktopublishedarticle" target="_blank">
      Name of the Scientific Paper The Simulation is Based On.
    </a>, <em>Max Mustermann and Martin Zacharias </em>.
{% endblock %}
 ```

### Update Homepage and Navbar Dropdown Menu
Finally, update home.html to include the new simulation on the gallery wall and alter the navbar dropdown menu in base.html to include your simulation.

Go to the Gallery portion of home.html and add a new div class below the others.
Consider how many simulations are already in one row. A row should contain no more than three columns. Open a new class row if there are currently three.
 ```html
        <div class="row">
          <div class="col-lg-4 mb-4 mb-lg-0">
            <a href="{% url 'job:newsim' %}"> <!--Add the url tag of your simulation-->
            <img
              src="{% static 'img/newsim.png' %}" 
              class="w-100 shadow-1-strong rounded mb-4 hover-shadow"
              alt="Name of Your Simulation" 
              style="object-fit: cover; opacity: 0.6; filter: brightness(50%)"
            /></a> <!--change the src variable to link to your selected image and change the alt variable-->
            <div class="caption">
              <h2 style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">Name of Your Simulation</h2>
              <!--Add the name of your simulation-->
            </div>
          </div>
        </div>
 ```
Navigate to the body of base.html and add a new dropdown item to include the simulation in the navbar dropdown menu.
 ```html
                 <li class="nav-item dropdown">
                  <a href="#" class="nav-link dropdown-toggle" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Submission</a>
                  <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                    <a class="dropdown-item" href="http://10.152.219.243/" target="_blank">Attract Online Server</a>
                    <a class="dropdown-item" href="{% url 'job:cpep' %}">cPEP Match Algorithm</a>
                    <a class="dropdown-item" href="{% url 'job:rsremd' %}">Replica Exchange with Repulsive Scaling</a>
                    <a class="dropdown-item" href="{% url 'job:newsim' %}">Name of Your Simulation</a> <!--All you have to do is add this line.-->
                  </div>
                </li>
 ```

### Add a Tutorial / User Guide
You may provide a guide on how to submit a job for this simulation. You simply need to navigate to./templates/help.html. Add a new article beneath the existing ones. There is nothing further that needs to be added to the HTML.
 ```html
   <article>
    <!--Enter the anchor name from newsim.html as well as the name of your simulation.-->
    <h2 id="anchor-name-for-newsim-tutorial">Name of Your Simulation</h2>
    <p>
      Create a brief instruction on how to submit a job and answer other frequently asked questions.
    </p>
    <hr>
  </article>
 ```