# Title     : Supervised learning
# Objective : Classification of Ocean Microbes
# Created by: jbeckles
# Created on: 23/01/2020
library(caret)
library(ggplot2)
library(rpart)
library(randomForest)
library(e1071)

setwd('C:/Users/jbeckles/OneDrive - Scott Logic Ltd/Documents/Personal/Coursera/DataScienceAtScale/DataManipulation/datasci_course_materials/assignment5')

# Read data set
records <- read.csv('seaflow_21min.csv')

# Answer to questions 1 and 2 (overall counts for each category of particle)
summary(records$pop)

# Answer for question 3 (equally split data into 'training' and 'testing')
record_count <- nrow(records)
indices <- 1:record_count
training_indices <- sample(indices, floor(record_count/2))
testing_indices <- indices[!indices %in% training_indices]

training <- list()
testing <- list()
col_ids <- names(records)
for (x in col_ids) {
  training[[x]] <- records[[x]][training_indices]
  testing[[x]] <- records[[x]][testing_indices]
}

training <- as.data.frame(training)
testing <- as.data.frame(testing)

# Answer for question 4
qplot(chl_small, pe, data = records, color = pop)

# Answer for questions 5, 6 and 7 (train a decision tree [model])
fol <- formula(pop ~ fsc_small + fsc_perp + fsc_big + pe + chl_big + chl_small)
decision_tree_model <- rpart(fol, method="class", data=training)
print(decision_tree_model)

# Answer for question 8 (obtain decision tree model accuracy)
get_model_accuracy <- function(prediction, test_data) {
  sum(prediction == test_data$pop) / nrow(test_data)
}
decision_tree_prediction <- predict(decision_tree_model, testing, 'class')
get_model_accuracy(decision_tree_prediction, testing)

# Answer for question 9 (obtain random forest model accuracy)
random_forest_model <- randomForest(fol, data=training)
random_forest_prediction <- predict(random_forest_model, testing, 'class')
get_model_accuracy(random_forest_prediction, testing)

# Answer for question 10
importance(random_forest_model)

# Answer for question 11 (obtain support vector machine model accuracy)
svm_model <- svm(fol, data=training)
svm_prediction <- predict(svm_model, testing)
get_model_accuracy(svm_prediction, testing)

# Answer for question 12
create_confusion_matrix <- function(prediction, test_data){
  dimension <- length(levels(prediction))
  result <- matrix(0, dimension, dimension)
  for(x in 1:nrow(test_data)){
    result[prediction[x], test_data$pop[x]] <- result[prediction[x], test_data$pop[x]] + 1
  }
  result
}
create_compare_table <- function(prediction, test_data){
  table(pred = prediction, true = test_data$pop)
}

decision_tree_confusion <- create_confusion_matrix(decision_tree_prediction, testing)
random_forest_confusion <- create_confusion_matrix(random_forest_prediction, testing)
svm_confusion <- create_confusion_matrix(svm_prediction, testing)

decision_tree_table <- create_compare_table(decision_tree_prediction, testing)
random_forest_table <- create_compare_table(random_forest_prediction, testing)
svm_table <- create_compare_table(svm_prediction, testing)

# Answer for question 13
val_id <- seq()
value <- seq()
col_id <- seq()
graph_cols <- c('fsc_small', 'fsc_perp', 'fsc_big', 'pe', 'chl_big', 'chl_small')
for(col in graph_cols) {
  interest_col <- records[[col]]
  val_id <- c(val_id, 1:record_count)
  value <- c(value, interest_col[order(interest_col)])
  col_id <- c(col_id, rep(col, record_count))
}

data_length <- length(graph_cols) * record_count + 1
final_data <- data.frame(val_id=val_id[2:data_length], value=value[2:data_length], col_id=as.factor(col_id[2:data_length]))
qplot(val_id, value, data = final_data, color = col_id)

# Answer for question 14
qplot(time, chl_big, data = records, color = pop)

# clean records of file 208 data
clean_records <- list()
clean_data_bools <- records$file_id != 208
for(col in col_ids) {
  clean_records[[col]] <- records[[col]][clean_data_bools]
}
clean_records <- as.data.frame(clean_records)

# perform experiments again
clean_record_count <- nrow(clean_records)
clean_indices <- 1:clean_record_count
training_indices <- sample(clean_indices, floor(clean_record_count/2))
testing_indices <- clean_indices[!clean_indices %in% training_indices]

clean_training <- list()
clean_testing <- list()
for (x in col_ids) {
  clean_training[[x]] <- clean_records[[x]][training_indices]
  clean_testing[[x]] <- clean_records[[x]][testing_indices]
}

clean_training <- as.data.frame(clean_training)
clean_testing <- as.data.frame(clean_testing)

decision_tree_model <- rpart(fol, method="class", data=clean_testing)
decision_tree_prediction <- predict(decision_tree_model, clean_testing, 'class')
get_model_accuracy(decision_tree_prediction, clean_testing)
create_confusion_matrix(decision_tree_prediction, clean_testing)

random_forest_model <- randomForest(fol, data=clean_testing)
random_forest_prediction <- predict(random_forest_model, clean_testing, 'class')
get_model_accuracy(random_forest_prediction, clean_testing)
create_confusion_matrix(random_forest_prediction, clean_testing)

svm_model <- svm(fol, data=clean_training)
svm_prediction <- predict(svm_model, clean_testing)
get_model_accuracy(svm_prediction, clean_testing)
create_confusion_matrix(svm_prediction, clean_testing)