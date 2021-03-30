"""Data wrangling of Boston and Seattle Airbnb Open Data
The module load data from csv file and prepare graphics with Plotly 
"""

import logging
import numpy as np
import os
import pandas as pd
import plotly.express as px
import re

# Collecting Data - Reading csv files
# The dataset was downloaded from the link 
# https://www.kaggle.com/airbnb/boston 
# https://www.kaggle.com/airbnb/seattle/data 
# 

def clean_data(df):
    """ Clean original data

    Arguments: 
    df: Pandas DataFrame

    Return:
    df: Pandas DataFrame after data cleaning
    """
    # Transform monetary columns that is originaly a string to float. <br>
    df['price'] = df['price'].astype(str) \
                             .apply(lambda x: re.sub('[$,]', '', x) if x is not None else x) \
                             .astype(float)


    # drop columns with less than 25% of the data filled
    thresh=df.shape[0]*.25
    df = df.dropna(thresh=thresh, axis=1)

    # remove the upper limit quantile
    upper_1_5_IQR = df.groupby('neighbourhood_cleansed')['price'].agg(
            lambda x: np.quantile(x, 0.75) + (np.quantile(x, 0.75) - np.quantile(x, 0.25))*1.5
            )
    upper_1_5_IQR = upper_1_5_IQR.to_dict()

    df['upper_1_5_IQR'] = df['neighbourhood_cleansed'].map(upper_1_5_IQR)

    df = df[df['price']<=df['upper_1_5_IQR']]
    df = df.drop(columns='upper_1_5_IQR')
    
    return df


def return_figures():
    df_boston_listings = pd.read_csv('data/boston/old/listings.csv')

    df_boston_listings = clean_data(df_boston_listings)


    # First chart plots Average Price by total people the house accommodates'
    hue='require_guest_phone_verification'
    prices_by_accommodates = df_boston_listings.groupby(['accommodates', hue])['price'] \
                                            .mean().reset_index()

    title='Average Price by total people the house accommodates'
    fig1 = px.line(prices_by_accommodates, x="accommodates", y="price", color=hue,
                title=title,labels={'price':'Average Price','require_guest_phone_verification':'guest_phone_verification'}
                )

    # Second chart plots Average Price by Neighbourhood
    mean_by_neighbourhood = df_boston_listings.groupby('neighbourhood_cleansed')['price']\
                                                    .mean().sort_values()\
                                                    .reset_index()
    title='Average Price by Neighbourhood'
    labels={'price':'Average Price', 'neighbourhood_cleansed':''}
    fig2 = px.bar(mean_by_neighbourhood, x='price', y='neighbourhood_cleansed', 
        orientation='h', title=title,labels=labels)

    # Third chart plots 'Charactiristics that influence price'
    price_correlation = df_boston_listings.corr()['price'].sort_values().iloc[:-2].reset_index()
    title='Characteristics that influence price'
    labels={'price':'Correlation Rate', 'index':''}
    fig3 = px.bar(price_correlation, x='price', y='index', 
                  orientation='h', title=title,
                  labels=labels)

    # Fourth chart shows Listings counts by price in each City

    # ### Loading Seattle dataset
    df_seattle_listings = pd.read_csv('data/seattle/old/listings.csv')
    df_seattle_listings = clean_data(df_seattle_listings)

    # merge Boston and Seattle data
    df_boston_listings['city_cleansed'] = 'Boston'
    df_seattle_listings['city_cleansed'] = 'Seattle'

    boston_prices = df_boston_listings[['price', 'city_cleansed']]
    seattle_prices = df_seattle_listings[['price', 'city_cleansed']]

    seattle_boston = boston_prices.append(seattle_prices)

    title = 'Listings counts by price <br>Each color is one city'
    labels = {'price':'Price','city_cleansed':'City'}
    fig4 = px.histogram(seattle_boston, x="price", color="city_cleansed", nbins=45,
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    title=title,labels=labels
                    )
    fig4.update_layout(barmode='overlay')
    fig4.update_traces(opacity=0.85)

    # append all charts to the figures list
    figures = []
    figures.append(fig1)
    figures.append(fig2)
    figures.append(fig3)
    figures.append(fig4)

    return figures



