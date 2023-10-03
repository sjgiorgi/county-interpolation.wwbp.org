import csv
import os

import pandas as pd
import numpy as np

import torch
import gpytorch

from sklearn.preprocessing import StandardScaler

cnty_str = 'FIPS'
training_iter = 500
learning_rate = 0.001

class ExactGPModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood):
        super(ExactGPModel, self).__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel())
    
    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

def interpolate_csv(filename, add_geo, add_twitter):
    try:
        df = csv_to_dataframe(filename)
        if add_geo:
            df = add_features(df, 'geo')
        if add_twitter:
            df = add_features(df, 'twitter')

        X_scaler, y_scaler = StandardScaler(), StandardScaler()

        spatial_unit_name = df.columns[0]
        y_column_name = df.columns[1]
        x_columns_names = df.columns[2:]

        

        # get training data and standardize
        df_train = df.dropna()
        X_train = df_train[x_columns_names].to_numpy()
        y_train = df_train[y_column_name].to_numpy().reshape(-1, 1)

        X_train = X_scaler.fit_transform(X_train)
        y_train = y_scaler.fit_transform(y_train)

        counties_train = list(df_train[spatial_unit_name].values)

        # get data to interpolate and standardize
        df_interpolate = df[df[y_column_name].isnull()]
        df_interpolate = df_interpolate[[spatial_unit_name]+list(x_columns_names)].dropna()
        
        X_interpolate = df_interpolate[x_columns_names].to_numpy()
        X_interpolate = X_scaler.transform(X_interpolate)

        counties_interpolate = list(df_interpolate[spatial_unit_name].values)

        # convert to tensors
        X_train = torch.from_numpy(X_train).float()
        y_train = torch.from_numpy(np.array([float(y[0]) for y in y_train])).float()
        
        X_interpolate = torch.from_numpy(X_interpolate).float()

        # train model
        likelihood = gpytorch.likelihoods.GaussianLikelihood()
        model = ExactGPModel(X_train, y_train, likelihood)

        model.train()
        likelihood.train()

        # Use the adam optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)  # Includes GaussianLikelihood parameters

        # "Loss" for GPs - the marginal log likelihood
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

        for i in range(training_iter):
            # Zero gradients from previous iteration
            optimizer.zero_grad()
            
            # Output from model
            output = model(X_train)
            
            # Calc loss and backprop gradients
            loss = -mll(output, y_train)
            loss.backward()
            print('Iter %d/%d - Loss: %.3f   lengthscale: %.3f   noise: %.3f' % (
                                    i + 1, training_iter, loss.item(),
                                    model.covar_module.base_kernel.lengthscale.item(),
                                    model.likelihood.noise.item()
                                ))

            optimizer.step()
        
        model.eval()
        likelihood.eval()

        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            observed_pred = likelihood(model(X_interpolate))
        y_interpolations = observed_pred.mean.numpy()
        y_std = observed_pred.stddev.detach().numpy()
        
        lengthscale = model.covar_module.base_kernel.lengthscale.item()

        output_file = write_to_csv(y_column_name, counties_interpolate, y_interpolations, y_std, lengthscale)
        return output_file
    except:
        return ""

def write_to_csv(column_name, counties, interpolations, std_devs, lengthscale):
    header = [cnty_str, column_name + "_interpolated", column_name + "_stddev"]
    output_file = "interpolations_ls%.3f.csv" % lengthscale
    
    with open(os.path.join('output', output_file), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for ii in range(len(counties)):
            writer.writerow([counties[ii], interpolations[ii], std_devs[ii]])
    return output_file

def csv_to_dataframe(filename):
    df = pd.read_csv(filename)
    return df

def clean_uploaded_data(df):
    # remove rows where spatial identifier is null
    df = df[~df[df.columns[0]].isnull()]

    # replace NA with empty strings

    # convert all columns to float
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c])

    return df

def add_features(df, feature_type):
    if feature_type == "geo":
        filename = "features/geo_features.csv"
    elif feature_type == "twitter":
        filename = "features/twitter_features.csv"
    df_feat = pd.read_csv(filename)
    df_feat['FIPS'] = df_feat['FIPS'].astype(str).str.rjust(5, '0')
    df_feat = df_feat.set_index('FIPS')

    df_index_name = df.columns[0]
    df['FIPS'] = df[df_index_name].astype(str).str.rjust(5, '0')
    df = df.set_index(df_index_name)
    if df_index_name != cnty_str:
        df = df.drop(columns=[df_index_name])
    
    df_joined = pd.concat([df, df_feat], axis=1)

    number_of_rows = df_joined.shape[0]
    if number_of_rows >= df_feat.shape[0] + df.shape[0]:
        # join did not work
        return df.reset_index()
    else:
        return df_joined.reset_index()
