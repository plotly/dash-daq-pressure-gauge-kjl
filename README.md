# dash-daq-pressure-gauge-kjl

## Introduction
`dash-daq-pressure-gauge-kjl` is a repository created to interface Kurt J. Lesker pressure gauges controllers with dash DAQ.

1. Kurt. J. Lesker MGC4000 multi-gauge controller
[Demo app on Heroku](https://dash-daq-pressure-gauge-kjl.herokuapp.com/), and dashdaq.io [blog post](https://www.dashdaq.io/read-pressure-from-kurt-j-lesker-gauge-controller-in-python)

### [Technique/field associated with the instrument]
Low pressure gauges (1 atmosphere and below) are used in vacuum environments. 

### dash-daq
[Dash DAQ](http://dash-daq.netlify.com/#about) is a data acquisition and control package built on top of Plotly's [Dash](https://plot.ly/products/dash/).


## Requirements
It is advisable	to create a separate virtual environment running Python 3 for the app and install all of the required packages there. To do so, run (any version of Python 3 will work):

```
python3 -m virtualenv [your environment name]
```
```
source activate [your environment name]
```

To install all of the required packages to this environment, simply run:

```
pip install -r requirements.txt
```

and all of the required `pip` packages, will be installed, and the app will be able to run.


## How to use the app

To control your gauge controller, you need to input your COM port number in the `app.py` file and set the `mock` attribute to `False`

```
pressure_gauge = MGC4000(
	instr_port_name=[your instrument's com port],
	mock=False, 
	gauge_dict={'CG1': 'mbar', 'CG4': 'mbar'}
)
```

Your gauges in `gauge_dict` should be named after the convention `[Gauge type][Gauge number]`. The gauge types implemented up to now are the following two types `'CG', 'IG'`. 

`CG` stands for "Convection gauge" and is a Pirani pressure gauge valid in the pressure range 1.3e-4 to 1333 mbar.

`IG` stands for "Ion gauge" and is a cathode ion gauge valid in the pressure range 1.3e-9 to 6.7e-2 mbar.

You can then run the app :

```
$ python app.py
```

if you don't have the instrument connected to your computer but would still like to test the app you can run

```
$ python app_mock.py
```

You can also set the `mock` attribute to `True` in the `app.py` file.


## Resources

Manual of the KJL [MGC4000](https://www.lesker.com/newweb/gauges/pdf/manuals/mgc4000usermanual.pdf)
