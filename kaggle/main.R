# Title            : Digit Recognizer
# Objective        : Classification of hand-written numbers (single digits)
# Problem Spec URL : https://www.kaggle.com/c/digit-recognizer
library(tidyverse)
library(e1071)
library(class)
library(stats)

# Application Constants
image_width <- 28
image_width_index <- image_width - 1

# Helper Functions
split_data <- function(input_data, training_percentage = 0.5){
  record_count <- nrow(input_data)
  indices <- 1:record_count
  training_indices <- sample(indices, floor(record_count * training_percentage))
  testing_indices <- indices[-training_indices]

  res <- list()
  res$train <- list()
  res$test <- list()
  col_ids <- names(input_data)
  for (x in col_ids) {
    res$train[[x]] <- input_data[[x]][training_indices]
    res$test[[x]] <- input_data[[x]][testing_indices]
  }

  res$train <- as.data.frame(res$train)
  res$test <- as.data.frame(res$test)
  res
}

get_prediction_accuracy <- function(prediction, test_data, col) {
  sum(prediction == test_data[[col]]) / nrow(test_data)
}

make_svm_prediction <- function(train, test){
  svm_model <- svm(label ~ ., data=train)
  predict(svm_model, test)
}

make_knn_prediction <- function(train, test){
  knn(subset(train, select = -label), test, train$label, k=3)
}

get_model_accuracy <- function(train, test, make_prediction){
  prediction <- make_prediction(train, subset(test, select = -label))
  get_prediction_accuracy(prediction, test, 'label')
}

find_image_left_border <- function(image){
  done <- FALSE
  res <- 0
  for(j in 0:image_width_index){
    for(i in 0:image_width_index){
      indx <- i * image_width + j
      if(image[[paste0('pixel', indx)]] > 0){
        res <- j
        done <- TRUE
        break
      }
    }

    if(done) {
      break
    }
  }
  res
}

find_image_top_border <- function(image){
  done <- FALSE
  res <- 0
  for(i in 0:image_width_index){
    for(j in 0:image_width_index){
      indx <- i * image_width + j
      if(image[[paste0('pixel', indx)]] > 0){
        res <- i
        done <- TRUE
        break
      }
    }

    if(done) {
      break
    }
  }
  res
}

shift_image <- function(image, left_shift, up_shift) {
  total_shift <- up_shift * image_width + left_shift
  for(i in 0:(image_width_index - up_shift)){
    for(j in 0:(image_width_index - left_shift)){
      indx <- i * image_width + j
      target_col <- paste0('pixel', indx)
      source_col <- paste0('pixel', indx + total_shift)
      image[[target_col]] <- ifelse(image[[source_col]] > 0, 128, 0)
      image[[source_col]] <- 0
    }
  }
  image
}

preprocess_data <- function(raw_data) {
  # Shift images to top-left of screen
  for(x in 1:nrow(raw_data)) {
    image <- raw_data[x,]
    raw_data[x,] <- shift_image(image, find_image_left_border(image), find_image_top_border(image))
  }

  # perform PCA on raw data
  # prcomp(raw_data)
  # pca_labelled <- cbind(label = processed_labelled$label, as.data.frame(prcomp(subset(processed_labelled, select = -label))$x))

  # drop all zero-valued columns
  non_zero_cols <- vector()
  row_count <- image_width * image_width
  pixel_col_names <- paste0(rep('pixel', row_count), 0:(row_count - 1))
  for (col in pixel_col_names) {
    total_pixel_val <- sum(raw_data[[col]])
    if(total_pixel_val != 0) {
      non_zero_cols <- append(non_zero_cols, col)
    }
  }
  raw_data[non_zero_cols]
}

print_image <- function(image_data){
  img <- matrix(0, image_width, image_width)
  for(i in 0:image_width_index){
    for(j in 0:image_width_index){
      indx <- i * image_width + j
      img[i+1, j+1] <- ifelse(image_data[[paste0('pixel', indx)]] > 0, 128, 0)
    }
  }
  print(image_data$label)
  print(img)
}

print_lost_pixels <- function(raw_data){
  clean_data <- pre_process_data(raw_data)
  col_ids <- as.integer(substring(names(clean_data), 6))
  matr_row <- floor(col_ids / image_width)
  matr_col <- col_ids %% image_width

  img <- matrix('X', image_width, image_width)
  for(x in 1:length(col_ids)){
    img[matr_row[x], matr_col[x]] <- '0'
  }
  print(img)
}

# 1) Read in data
# training <- read.csv('../input/digit-recognizer/train.csv')

setwd('C:/Users/jbeckles/OneDrive - Scott Logic Ltd/Documents/Personal/Coursera/DataScienceAtScale/DataManipulation/datasci_course_materials/kaggle')
labelled <- read.csv('train.csv')
unlabelled <- read.csv('test.csv')
print('files read')

# 2) Inspect data
# test <- head(labelled)
# for(x in 1:nrow(test)) {
#   image_data <- test[x,]
#   img <- matrix(0, image_width, image_width)
#   for(i in 0:image_width_index){
#     for(j in 0:image_width_index){
#       indx <- i * image_width + j
#       img[i+1, j+1] <- ifelse(image_data[[paste0('pixel', indx)]] > 0, 100, 0)
#     }
#   }
#   print(image_data$label)
#   print(img)
# }
# hist(labelled$label, col='green')


# 2) Train model and test accuracy
#split_labelled <- split_data(labelled, 0.6)
# Sys.time()
# get_model_accuracy(split_labelled$train, split_labelled$test, make_knn_prediction)
# Sys.time()
# get_model_accuracy(split_labelled$train, split_labelled$test, make_svm_prediction)
# Sys.time()

# 3) Solve problem
results <- make_knn_prediction(labelled, unlabelled)
print('prediction made')
output <- cbind(ImageId= 1:length(results), Label=(as.numeric(results) - 1))
write.csv(output, file = 'results.csv', row.names = FALSE)


## Saving data

# If you save any files or images, these will be put in the "output" directory. You
# can see the output directory by committing and running your kernel (using the
# Commit & Run button) and then checking out the compiled version of your kernel.