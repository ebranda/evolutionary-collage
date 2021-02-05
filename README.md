# Evolutionary Collage

## To install and run this Processing sketch for the first time

1. Go to the [latest releases page](https://github.com/ebranda/evolutionary-collage/releases) and download the most recent release. Unzip the file and rename the folder `Evolutionary Collage` (this is important). Move the renamed folder to your Processing sketchbook (in _[home] > Documents > Processing_ by default).
2. Navigate into the `Evolutionary Collage` folder and create the following empty folder structure:
  - `data`
	  - `comparator_samples`
      - `parts`
3. Place your figure-ground diagram inside `comparator_samples` and place your parts images inside `parts`.
4. Launch Processing and open the `Evolutionary Collage` sketch. 
5. Edit the default settings in `settings.py` file as desired. Run the sketch.
6. Navigate to `data/runs/[run-number]` to view the results. The outputs folder contains the result images. The inputs folder contains copies of the input images used for this run. The `settings.py` file is an exact copy of the settings file used for this run. To restore the input images and settings at a later date, simply copy `settings.py` to the main `Evolutionary Collage` sketch folder and the input images to their respective folders in `Evolutionary Collage/data`.

Note that you can add named folders inside `Evolutionary Collage/data` to better manage your projects. Simply create an empty folder (e.g. `myapp`) in `Evolutionary Collage/data` and place your `comparator_samples` and `parts` image folders inside that folder. Then edit the variable `app.data_folder_name` in `settings.py` so that `None` is changed to `"myapp"`. You can switch between subprojects by editing `settings.py` again.


### To install updated code

This process involves installing the latest release as a new sketch in your Processing sketchbook, and then moving your existing data folder and settings file into the new sketch.

1. Navigate to your Processing sketchbook folder (_[home] > Documents > Processing_ by default). Rename the `Evolutionary Collage` folder to `Evolutionary Collage_OLD`.
2. Follow step 1) in the section *To install and run this Processing sketch* above to install the latest release.
4. Open your old sketch folder that you renamed in step 1 (`Evolutionary Collage_OLD`) and move the `data` folder and the `settings.py` file to the new sketch folder (`Evolutionary Collage`).


### To send your Processing sketch for feedback or bug fixes

1. Navigate to your Processing sketchbook folder (_[home] > Documents > Processing_ by default). Duplicate the `Evolutionary Collage` folder and give it a new name (e.g. `Evolutionary Collage_COPY`).
2. Open the `data` folder inside `Evolutionary Collage_COPY`. Make sure that the images inside `comparator_samples` and `parts` are correct. Delete any additional subproject folders (see above). Delete the `runs` folder.
3. Make sure that your `Evolutionary Collage/settings.py` file is correct.
3. Zip the entire `Evolutionary Collage` folder and email it to your instructor.


### To draw a background before parts are rendered:

1. Create a new Python module called `background.py`. The main Processing sketch will automatically import that module if it exists.
2. Inside that module, define a function called `draw(params, canvas)`. Do any background rendering inside that function. For example, the following code will draw a black background in the top half of the canvas window:

```
def draw(params, canvas):
  canvas.fill(0)
  canvas.rect(0, 0, canvas.width, canvas.height/2)
```


### To define your own fitness function:

1. Create a new Python module called `fitness.py`. The main Processing sketch will automatically import that module if it exists.
2. Inside that module, define a function called `compute_fitness(phenotype)`. For example, the following code will return a fitness score based on the average pixel grayscale value across all pixels in an image:

```
def compute_fitness(phenotype):
  graytotal = 0
  for px in phenotype.pixels:
    graytotal += brightness(px)
  mean = graytotal / len(phenotype.pixels) / 255.0
  return mean
```
