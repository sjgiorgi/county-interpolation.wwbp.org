# Web Interface for county-interpolation.wwbp.org

This is a simple web interface which allows you to run Gaussian Process regressions for interpolation over spatial data.

# Methods

Input data has three types of columns:

1. The first column is the **unique spatial identifier** for the row. For example, this can be a U.S. county FIPS code, a U.S. state name, etc. We assume this value is unique to each row and not repeated across the CSV file.
2. The second column is the **outcome** which you wich to interpolate.
3. The remaining columns (the third through the last column) are the **feature** columns. These data points are used to create the interpolation space. For example, this can include geographic features (such as latitude and longitude coordinates) or socio-demographic features (such as education rates or population statistics like percent urban/rural).  

The full interpolation process is as follows:

1. Drop all rows where there are any missing values in the feature columns (the 3rd through last columns of the csv).
2. Train a Gaussian Process model on all rows where the outcome column has non-missing data (the second column).
    
    2a. We use a Radial Basis kernel function (also known as a squared exponential) with a single lengthscale parameter. This parameter is learned from the training data.

    2b. Optionally add the Twitter and/or geographic features to the interpolation space.

    2c. We train the Gaussian Process model by iterating over the trainin data 500 times.

3. Apply the Gaussian Process model to any rows where the outcome column is missing (i.e. interpolate where the outcome is missing and the features are known).

4. Return the predictions from the Gaussian Process model. We return both the mean value of the distribution at each point (i.e., the interpolation) and the standard deviation at each point (i.e., the uncertainty). 



## Citation

If you use this tool in your work please cite the following [paper]():

```
@inproceedings{giorgi2022interpolation,
        title={County Interpolation},
        author={Giorgi, Salvatore and Eichstaedt, Johannes C and Gardner, Jacob R and Schwartz, H Andrew  and Ungar, Lyle},
        url={county-interpolation.wwbp.org},
}
```

## License

Licensed under a [GNU General Public License v3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Background

Developed by the [World Well-Being Project](http://www.wwbp.org) based out of the University of Pennsylvania, Stanford University, and Stony Brook University. 
