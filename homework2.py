# PPHA 30537
# Spring 2024
# Homework 2

# Charles Huang
# chuang2

# Due date: Sunday April 21st before midnight
# Write your answers in the space between the questions, and commit/push only
# this file to your repo. Note that there can be a difference between giving a
# "minimally" right answer, and a really good answer, so it can pay to put
# thought into your work.  Using functions for organization will be rewarded.

##################

# To answer these questions, you will use the csv document included in
# your repo.  In nst-est2022-alldata.csv: SUMLEV is the level of aggregation,
# where 10 is the whole US, and other values represent smaller geographies. 
# REGION is the fips code for the US region. STATE is the fips code for the 
# US state.  The other values are as per the data dictionary at:
# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2020-2022/NST-EST2022-ALLDATA.pdf
# Note that each question will build on the modified dataframe from the
# question before.  Make sure the SettingWithCopyWarning is not raised.




# PART 1: Macro Data Exploration

# Question 1.1: Load the population estimates file into a dataframe. Specify
# an absolute path using the Python os library to join filenames, so that
# anyone who clones your homework repo only needs to update one for all
# loading to work.


import pandas as pd
import us
nst = pd.read_csv("/Users/charleshuang/Documents/GitHub/data_skills_1_hw2/NST-EST2022-ALLDATA.csv")




# Question 1.2: Your data only includes fips codes for states (STATE).  Use 
# the us library to crosswalk fips codes to state abbreviations.  Drop the
# fips codes.

#To install library, run pip install us on terminal first

from us import states

#====

def state_find(fips):
    my_state = us.states.lookup(str(fips))
    if my_state is not None:
        return my_state.abbr
    else: 
        return "N/A"
    
nst['st_abbreviation'] = nst['STATE'].apply(state_find)
    
#drop removes a column from a df)
nst = nst.drop('STATE', axis=1)



# Question 1.3: Then show code doing some basic exploration of the
# dataframe; imagine you are an intern and are handed a dataset that your
# boss isn't familiar with, and asks you to summarize for them.  Do not 
# create plots or use groupby; we will do that in future homeworks.  
# Show the relevant exploration output with print() statements.

print(nst.head()) #prints first 5 rows
print(nst.tail()) #prints last 5 rows

nst_shape = nst.shape
print(nst_shape) #prints dimensions of data frame

nst.dtypes #shows all data types in the data frame

print(nst.describe()) #show summary stats such as mean, std, IQR


# Question 1.4: Subset the data so that only observations for individual
# US states remain, and only state abbreviations and data for the population
# estimates in 2020-2022 remain.  The dataframe should now have 4 columns.

#Removes all observations that are about regions, etc. leaving only states
nst_subset = nst[(nst['st_abbreviation'] != 'N/A') ]

#Remove all columns other than the requested ones
nst_subset = nst_subset[['POPESTIMATE2020','POPESTIMATE2021','POPESTIMATE2022', 'st_abbreviation']]



# Question 1.5: Show only the 10 largest states by 2021 population estimates,
# in decending order.

#sort_values() allows sorting a dataframe by a column, with ascending=True or False
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
print(nst_subset.sort_values(by='POPESTIMATE2021', ascending=False).head(10)) #head prints first X rows



# Question 1.6: Create a new column, POPCHANGE, that is equal to the change in
# population from 2020 to 2022.  How many states gained and how many lost
# population between these estimates?

nst_subset["POPCHANGE"] = nst_subset["POPESTIMATE2022"] - nst_subset["POPESTIMATE2020"]

def count(x):
    pos = 0
    neg = 0
    for i in x:
        if i > 0:
            pos += 1
        elif i < 0:
            neg += 1
        else:
            pass
    return f"There are {pos} positive values and {neg} negative values."


count(nst_subset["POPCHANGE"])
#Out[46]: 'There are 25 positive values and 19 negative values.'
#Thus, there were 25 states that gained population and 19 that lost population.

# Question 1.7: Show all the states that had an estimated change in either
# direction of smaller than 1000 people. 

#can use abs() to indicate absolute value 
nst_1000 = nst_subset[abs(nst_subset['POPCHANGE']) < 1000]
print(nst_1000['st_abbreviation'])
            
#The states are Kansas and North Dakota (KS/ND)


# Question 1.8: Show the states that had a population growth or loss of 
# greater than one standard deviation.  Do not create a new column in your
# dataframe.  Sort the result by decending order of the magnitude of 
# POPCHANGE.

#To calculate standard deviation, use .std() method in pandas

def state_stdev(x):
    std_devs = x.iloc[ :, 0:3].std(axis=1) #calculates stdev of the values in the first 3 cols across each row, and returns a series
    abs_pop_change = abs(x['POPCHANGE']) #takes absolute value of population change
    state = x['st_abbreviation'] 
    std_df = pd.concat([std_devs, abs_pop_change, state], axis=1, keys=['sd', 'pchange', 'state']) #concat adds 2 series into a dataframe, keys renames the columns
    #https://pandas.pydata.org/docs/reference/api/pandas.concat.html
    std_df = std_df[std_df['sd'] < std_df['pchange']] #filters only observations where magnitude of pop growth was greater than one standard deviation
    return std_df
        
answer = state_stdev(nst_subset).sort_values(by='pchange', ascending=False).head(10)
print(answer)

#PART 2: Data manipulation

# Question 2.1: Reshape the data from wide to long, using the wide_to_long function,
# making sure you reset the index to the default values if any of your data is located 
# in the index.  What happened to the POPCHANGE column, and why should it be dropped?
# Explain in a brief (1-2 line) comment.

nst_long = pd.wide_to_long(nst_subset, 'POPESTIMATE', i = ['st_abbreviation', 'POPCHANGE'], j = "year", sep="")


print(nst_long.head())
nst_long = nst_long.drop('POPCHANGE', axis=1)

#Explanation: The POPCHANGE column was turned into three repeating values for each state. The column should be dropped since it no longer makes sense for each year to have the same population change.

# Question 2.2: Repeat the reshaping using the melt method.  Clean up the result so
# that it is the same as the result from 2.1 (without the POPCHANGE column).

nst_melted = nst_subset.melt(
    id_vars= ['st_abbreviation', 'POPCHANGE'],
    var_name='year',
    value_name='POPESTIMATE')

nst_melted = nst_melted.sort_values(by='st_abbreviation', ascending=True)
nst_melted = nst_melted.drop('POPCHANGE', axis=1)

print(nst_melted.head())

# Question 2.3: Open the state-visits.xlsx file in Excel, and fill in the VISITED
# column with a dummy variable for whether you've visited a state or not.  If you
# haven't been to many states, then filling in a random selection of them
# is fine too.  Save your changes.  Then load the xlsx file as a dataframe in
# Python, and merge the VISITED column into your original wide-form population 
# dataframe, only keeping values that appear in both dataframes.  Are any 
# observations dropped from this?  Show code where you investigate your merge, 
# and display any observations that weren't in both dataframes.

visited = pd.read_excel("/Users/charleshuang/Documents/GitHub/data_skills_1_hw2/state-visits.xlsx")

visited_nst = pd.merge(visited, nst_subset, left_on='STATE', right_on='st_abbreviation', indicator=True)

#We can display observations not in both dataframes by doing an outer join instead of an inner join and using the indicator arg

visited_nst_outer = pd.merge(visited, nst_subset, left_on='STATE', right_on='st_abbreviation', how="outer", indicator=True)

not_both = visited_nst_outer[visited_nst_outer["_merge"] != "both"]
#this shows all rows that weren't in both dataframes; eight rows were dropped
print(not_both)

# Question 2.4: The file policy_uncertainty.xlsx contains monthly measures of 
# economic policy uncertainty for each state, beginning in different years for
# each state but ending in 2022 for all states.  The EPU_National column esimates
# uncertainty from national sources, EPU_State from state, and EPU_Composite 
# from both (EPU-N, EPU-S, EPU-C).  Load it as a dataframe, then calculate 
# the mean EPU-C value for each state/year, leaving only columns for state, 
# year, and EPU_Composite, with each row being a unique state-year combination.


#Calculate the mean EPU-C value for each state/year, and leave only columns for state, year, and EPU composite. There will be multiple rows for each state.


epuc = pd.read_excel("/Users/charleshuang/Documents/GitHub/data_skills_1_hw2/policy_uncertainty.xlsx")

#We can use groupby() to calculate by state/year, and use .mean() to find the EPU_C mean value by group

group_epuc = epuc.groupby(['state', 'year']).mean()

#Note: Leaving month column no longer makes sense since the average month is "6.5" which is nonsensical, so drop it
group_epuc = group_epuc.drop(columns=['month','EPU_National', 'EPU_State'])

print(group_epuc)


# Question 2.5) Reshape the EPU data into wide format so that each row is unique 
# by state, and the columns represent the EPU-C values for the years 2022, 
# 2021, and 2020. 

#use loc to filter since groupby turns state and year into indices. The syntax takes 2 args since we grouped by two variables (two indices), and then the colon arg indicates we want to keep all columns.
epuc_20_22 = group_epuc.loc[slice(None), slice(2020, 2022), :]
  #Slice(None) selects all values in the state index and the second slice pulls all years within that range in the year index.
  


#Drop the other columns and only keep EPU-C
epuc_20_22 = epuc_20_22["EPU_Composite"]

  
#Now we need to change from long to wide so that the years are in different columns instead of the year column

epuc_20_22 = epuc_20_22.reset_index() #a function that takes away the indices made by groupby()
epuc_wide = epuc_20_22.pivot(index='state', columns='year', values='EPU_Composite')
epuc_wide.columns = ['EPU_C_2020', 'EPU_C_2021', 'EPU_C_2022']


# Question 2.6) Finally, merge this data into your merged data from question 2.3, 
# making sure the merge does what you expect.

#We need to convert full state names to abbreviations below.

#returning to this from a previous problem 
def state_find(fips):
    my_state = us.states.lookup(str(fips))
    if my_state is not None:
        return my_state.abbr
    else: 
        return "N/A"
    
#Now repeat the steps from the merge previously
epuc_wide = epuc_wide.reset_index()
    
epuc_wide['state'] = epuc_wide['state'].apply(state_find)

visited_nst = visited_nst.drop('_merge', axis=1)

visited_epuc = pd.merge(epuc_wide, visited_nst, left_on="state", right_on="STATE", how="outer", indicator=True)



# Question 2.7: Using groupby on the VISITED column in the dataframe resulting 
# from the previous question, answer the following questions and show how you  
# calculated them: 
#a) what is the single smallest state by 2022 population  
# that you have visited, and not visited?  
#b) what are the three largest states  
# by 2022 population you have visited, and the three largest states by 2022 
# population you have not visited? 
#c) do states you have visited or states you  
# have not visited have a higher average EPU-C value in 2022?

#We can use groupby() to calculate by state/year


#a. Smallest state by 2022 population that was visited
#To calculate, group by "VISITED" and use min() on POPESTIMATE2022 to find the smallest state in the VISITED=1 group
pd.set_option('display.max_columns', None)
grouped_states = visited_epuc.groupby('VISITED')



min_index = grouped_states['POPESTIMATE2022'].idxmin()
#idxmin() fetches the index of the row with the min. value of POPESTIMATE2022 by group
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.idxmin.html

#Now use this index to find the corresponding state:
print(visited_epuc.loc[min_index])
#The smallest state by 2022 population that was visited was Delaware (DE).

#b. To find three largest visited and non-visited states, use .get_group() and nlargest() to retrieve the groups separately and find the n largest values of 'POPESTIMATE2022'.
#getgroup(): essentially filters by group https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.get_group.html
#nlargest(): returns the first n rows when ordered by a column in descending order. This was found by searching online on how to return multiple rows with min() or max(). https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nlargest.html 

def get_states(visit_status, n): #visit_status is 0 or 1, n is the number of states with largest pop we want to find
    return grouped_states.get_group(visit_status).nlargest(n, 'POPESTIMATE2022')
        
print(get_states(1, 3)) #The three largest visited states are TX, FL, and NY

print(get_states(0, 3)) #The three largest non-visited states are GA, NC, and WA   


#c. Which has the higher average EPU-C value in 2022: visited or non-visited states?
epu_c_comparison = grouped_states['EPU_C_2022'].mean()
print(epu_c_comparison)
#VISITED
#0.0    212.246521
#1.0    214.634865
#Visited states have the higher EPU-C value in this case.


# Question 2.8: Transforming data to have mean zero and unit standard deviation
# is often called "standardization", or a "zscore".  The basic formula to 
# apply to any given value is: (value - mean) / std
# Return to the long-form EPU data you created in step 2.4 and then, using groupby
# and a function you write, transform the data so that the values for EPU-C
# have mean zero and unit standard deviation for each state.  Add these values
# to a new column named EPU_C_zscore.

#Reloading group_epuc from 2.4:
    
group_epuc = epuc.groupby(['state', 'year']).mean()
group_epuc = group_epuc.reset_index() 
group_epuc = group_epuc.drop(columns=['month','EPU_National', 'EPU_State'])



def stdz(group): 
    #Calculate the mean and std deviation of each state since groupby() was already used
    mean = group.mean()
    std = group.std()
    #Calculate the z score using the variables above, and add it to a new column titled EPU_C_zscore
    zscores= (group - mean) / std
    #return the dataframe
    return zscores
    
group_epuc['EPU_C_zscore'] = group_epuc.groupby('state')['EPU_Composite'].transform(stdz)


#transform is similar to apply in that it applies a function to multiple things, but apply operates on entire dataframe while transform applies to groups/subsets
#https://stackoverflow.com/questions/27517425/whether-to-use-apply-vs-transform-on-a-group-object-to-subtract-two-columns-and

print(group_epuc)

#a quick test to see if the mean of the z-scores is 0
test = group_epuc.query('state == "Alabama"')
testlist = test['EPU_C_zscore']
print(testlist.mean())

#-3.885780586188048e-16
