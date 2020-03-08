library(tidyverse)
library(ggplot2)

setwd('C:/Users/jbeckles/OneDrive - Scott Logic Ltd/Documents/Personal/Coursera/DataScienceAtScale/datasci_course_materials/assignment6')
seattle <- read.csv('seattle_incidents_summer_2014.csv')
sanfrancisco <- read.csv('sanfrancisco_incidents_summer_2014.csv')

weekday_levels <- c('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
normalise_seattle <- function(seattle) {
  date_time <- strptime(as.character(seattle$Occurred.Date.or.Date.Range.Start), format = '%m/%d/%Y %I:%M:%S %p')

  cat <- as.character(seattle$Summarized.Offense.Description)
  # to include as part of modified function
  cat <- ifelse(cat %in% c('BIKE THEFT','CAR PROWL','MAIL THEFT','SHOPLIFTING'), 'LARCENY/THEFT', cat)
  cat <- ifelse(cat %in% 'NARCOTICS', 'DRUG/NARCOTIC', cat)
  cat <- ifelse(cat %in% 'WARRANT ARREST', 'WARRANTS', cat)

  data.frame(
    City = as.character(rep('Seattle', nrow(seattle))),
    DayOfWeek = factor(weekdays(date_time), levels=weekday_levels),
    Hour = as.numeric(date_time$hour),
    Category = cat
  )
}

normalise_sanfrancisco <- function (sanfrancisco) {
  cat <- as.character(sanfrancisco$Category)
  cat <- ifelse(cat %in% 'VANDALISM', 'OTHER PROPERTY', cat)

  data.frame(
    City = as.character(rep('San Francisco', nrow(sanfrancisco))),
    Hour = as.numeric(substring(as.character(sanfrancisco$Time),1,2)),
    DayOfWeek = factor(sanfrancisco$DayOfWeek, levels=weekday_levels),
    Category = cat
  )
}

summarise_data <- function(data) {
  as.data.frame(data %>% group_by(Category) %>% summarise(Incidents = n()))
}

get_large_categories <- function(summarised_data) {
  top_cats <- summarised_data %>% top_n(5, Incidents)
  unique(as.character(top_cats$Category))
}

extract_large_categories <- function(summarised_seattle, summarised_sanfrancisco) {
  cats_seattle <- get_large_categories(summarised_seattle)
  cats_sanfrancisco <- get_large_categories(summarised_sanfrancisco)

  unique(c(cats_seattle, cats_sanfrancisco))
}

normal_seattle <- normalise_seattle(seattle)
normal_sanfrancisco <- normalise_sanfrancisco(sanfrancisco)

summarised_seattle <- summarise_data(normal_seattle)
summarised_sanfrancisco <- summarise_data(normal_sanfrancisco)

filter_cats <- extract_large_categories(summarised_seattle,summarised_sanfrancisco)
result_data <- rbind(normal_seattle, normal_sanfrancisco)
result_data <- result_data[result_data$Category %in% filter_cats,]
result_data$Category = as.factor(as.character(result_data$Category))
result_data$Hour = as.factor(result_data$Hour)

grouped_bar_data <- as.data.frame(result_data %>% group_by(City, DayOfWeek, Hour, Category) %>% summarise(Incidents = n()))

# comparison of Major crimes by city
ggplot(grouped_bar_data, aes(fill=City, y=Incidents, x=Category)) + geom_bar(position="dodge", stat="identity")

# comparison of Crime Time (DayOfWeek/Hour) by city
ggplot(grouped_bar_data, aes(fill=City,y=Incidents, x=Hour)) + facet_grid(DayOfWeek ~ City) + geom_bar(stat='identity', show.legend = FALSE)

# Deeper inspection of 12pm crime spike by city
time_filtered <- grouped_bar_data[as.integer(as.character(grouped_bar_data$Hour)) %in% 10:14,]
ggplot(time_filtered, aes(fill=City,y=Incidents, x=Hour)) + facet_grid(City ~ Category) + geom_bar(position="dodge",stat='identity', show.legend = FALSE)
