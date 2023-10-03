# Web Interface for county-interpolation.wwbp.org

This is a simple web interface which allows you to run Gaussian Process regressions for interpolation over spatial data. We use [GPytorch](https://www.gnu.org/licenses/gpl-3.0.en.html) to implement the Gaussian Process regressions.

# Methods

## Data formatting

Input data has three types of columns:

1. The first column is the **unique spatial identifier** for the row. For example, this can be a U.S. county FIPS code, a U.S. state name, etc. We assume this value is unique to each row and not repeated across the CSV file.
2. The second column is the **outcome** which you wich to interpolate.
3. The remaining columns (the third through the last column) are the **feature** columns. These data points are used to create the interpolation space. For example, this can include geographic features (such as latitude and longitude coordinates) or socio-demographic features (such as education rates or population statistics like percent urban/rural).  

### Example data

We [include a CSV](https://github.com/sjgiorgi/county-interpolation.wwbp.org/blob/master/static/example_data.csv) with county-level personality (Big 5 agreeableness) and socio-demographic features as an example. County-level agreeableness is estimated from Twitter data and taken from this [paper](http://doi.org/10.1111/jopy.12674). 

With the exception of agreeableness, this example data is the same data used in our original manuscript on interpolation with Gaussian Processes and social media data (paper TBA). While the original paper used life satisfaction as the outcome to be interpolated, due to restrictions on data sharing, we have replaced life satisfaction with agreeableness. 

## Interpolation process

The full interpolation process is as follows:

1. Drop all rows where there are any missing values in the feature columns (the 3rd through last columns of the csv).
2. Train a Gaussian Process model on all rows where the outcome column has non-missing data (the second column).
    
    2a. We use a Radial Basis kernel function (also known as a squared exponential) with a single lengthscale parameter. This parameter is learned from the training data.

    2b. Optionally add the Twitter and/or geographic features to the interpolation space.

    2c. We train the Gaussian Process model by iterating over the training data 500 times.

3. Apply the Gaussian Process model to any rows where the outcome column is missing (i.e. interpolate where the outcome is missing and the features are known).

4. Return the predictions from the Gaussian Process model. We return both the mean value of the distribution at each point (i.e., the interpolation) and the standard deviation at each point (i.e., the uncertainty). 


## Optional parameters

We offer these two data sources for U.S. counties only. 

### Twitter features

We use set of 2,000 topics (or group of semantically related words, as derived from Latent Dirichlet Allocation, LDA) as features for interpolating. These topics have been dimensionally reduced via principal component analysis (PCA) to 25 dimenions. Other sets of PCA features (10, 15, 50, and 100 dimensions) are available [here](https://osf.io/edjak/?view_only=1ce6f885228747ffaa8a823eb17fde26), though the 25 dimensions were found to consistently produce accuracte interpolations even when training a Gaussian Process model on a small number of observations. 

The U.S. county topic loadings are taken from the [County Tweet Lexical Bank](https://github.com/wwbp/county_tweet_lexical_bank) and were dervied from 1.5 billion tweets from approximately 6 million geolocated Twitter users. 

These features are available for 2,041 U.S. counties.

### Geographic features

The latitude and longitude coordinates of U.S. county centroids are available as features. While on their own they do not build a strong interpolation space, when added on top of additional features (such as socio-demographics or Twitter), we found that they consistently increase the interpolation accuracy. 

These features are available for 3,143 U.S. counties.

## Frequently Asked Questions (FAQ)

1. Does this tool work for non-U.S. county data?

Yes, this tool will work for any data. The tool simply builds a Gaussian Process model over the supplied data, and is thus agnostic to the spatial layout of the data. If you would like this model to consider physical space then you must supply this measure in the uploaded CSV. For example, this can be latitude and longitude coordinates of the centroid of your spatial units.  

2. Does this tool work for larger spatial units, such as U.S. states?

We recommend this tool for smaller spatial units for which you have a reasonable number of observations. Larger spatial units present a problem in that there are fewer observations, for example, 50 U.S. states as opposed to over 3,000 U.S. counties. This means there are less observations used to train the Gaussian Process model. Given a smaller number of observations, the Gaussian Process model may fail to converge and, thus, the interpolations may be noisy. 

3. Does the FIPS code need a specific formatting in order to use the additional features packaged with this tool (Twitter topics or latitude/longitude coordinates)?

The FIPS code in the first column can be either a string (e.g., '42101') or numeric (e.g., 42101). The backend will convert this to a string and pad preceeding zeros as needed (since FIPS codes are 5 digits). For example, the numeric FIPS code 1001 will be converted to the string '01001'. Deviations from this formating with cause the backend to fail. 


## Citation

If you use this tool in your work please cite the following [paper]():

```
@inproceedings{giorgi2022interpolation,
    title={County Interpolation},
    author={Giorgi, Salvatore and Eichstaedt, Johannes C and Gardner, Jacob R and Schwartz, H Andrew and Ungar, Lyle},
    url={county-interpolation.wwbp.org},
}
```

## License

Licensed under a [GNU General Public License v3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Background

Developed by the [World Well-Being Project](http://www.wwbp.org) based out of the University of Pennsylvania, Stanford University, and Stony Brook University. 
