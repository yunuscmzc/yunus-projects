# Load necessary libraries
library(httr)
library(jsonlite)
library(dplyr)
library(lubridate)
library(tidyr)
library(stringr)
library(readr)
library(purrr)

#' Get Historical Weather Data from Open-Meteo API
#'
#' Retrieves historical weather data (archive or forecast history).
#' Latest available data is typically up to two days ago.
#'
#' @param start_date Character string. Start date in "YYYY-MM-DD" format.
#' @param variables Character vector. Hourly weather parameters to retrieve.
#' @param coordinates List of numeric vectors. Each inner vector is c(latitude, longitude).
#' @param get_forecast_data Logical. If TRUE, retrieves history of forecast data.
#'                          If FALSE, retrieves actual historical weather data (archive).
#' @param ... Additional API parameters (passed as named arguments).
#'
#' @return A data frame (tibble) with datetime ('dt') and weather variables
#'         for each location, combined column-wise.
#'
#' @examples
#' \dontrun{
#' coords <- list(c(41.01, 28.98), c(39.93, 32.86)) # Istanbul, Ankara
#' vars <- c("temperature_2m", "relative_humidity_2m")
#' hist_data <- get_historical_weather("2023-01-01", vars, coords, get_forecast_data = FALSE)
#' }
get_historical_weather <- function(start_date, variables, coordinates, get_forecast_data = TRUE, ...) {
    # Determine API URL based on data type request
    actual_past_url <- "https://archive-api.open-meteo.com/v1/archive"
    forecast_past_url <- "https://historical-forecast-api.open-meteo.com/v1/forecast"
    api_url <- if (get_forecast_data) forecast_past_url else actual_past_url

    # Calculate end date (2 days before today)
    end_date <- format(Sys.Date() - days(2), "%Y-%m-%d")

    all_dataframes <- list()
    additional_api_params <- list(...)

    # Loop through each coordinate pair
    for (i in seq_along(coordinates)) {
        coord <- coordinates[[i]]
        latitude <- coord[1]
        longitude <- coord[2]

        # Base parameters
        params <- list(
            latitude = latitude,
            longitude = longitude,
            start_date = start_date,
            end_date = end_date,
            hourly = paste(variables, collapse = ","), # API expects comma-separated string
            timezone = "Europe/Istanbul" # Explicitly set timezone, matches Python example
        )

        # Add any extra parameters provided via ...
        if (length(additional_api_params) > 0) {
            params <- c(params, additional_api_params)
        }

        # Make the API request
        response <- GET(api_url, query = params)

        # Check for HTTP errors
        stop_for_status(response, task = paste("fetch historical weather data for coord", i))

        # Parse the JSON response
        content <- content(response, "text", encoding = "UTF-8")
        data <- fromJSON(content, flatten = TRUE)

        if (!is.null(data$hourly) && length(data$hourly$time) > 0) {
            # Extract hourly data
            hourly_data <- as_tibble(data$hourly)

            # Convert time column to POSIXct (datetime)
            # API returns times in ISO8601 format T Z (e.g., "2023-01-01T00:00Z")
            # Or sometimes as strings like "2022-01-01T00:00" if timezone param is used
            # as_datetime should handle ISO8601; force timezone if needed
            hourly_data$time <- ymd_hm(hourly_data$time, tz = "Europe/Istanbul") # Ensure correct TZ

            # Rename columns to match Python output format: location_XXX variable
            location_prefix <- paste0("location_", str_pad(i - 1, 3, pad = "0"), ".") # Python uses 0-based index
            names(hourly_data) <- case_when(
                names(hourly_data) == "time" ~ "dt",
                TRUE ~ paste0(location_prefix, names(hourly_data))
            )

            all_dataframes[[i]] <- hourly_data
        } else {
            warning(paste("No hourly data returned for coordinate", i, "- Lat:", latitude, "Lon:", longitude))
            # Create an empty placeholder if needed, or handle appropriately
            # For simplicity here, we just warn and skip adding it.
            # Consider creating a tibble with just 'dt' if joining structure is critical
        }
    }

    # Combine all data frames by the 'dt' column
    if (length(all_dataframes) > 0) {
        # Use reduce with full_join to merge all tibbles by 'dt'
        combined_df <- reduce(all_dataframes, full_join, by = "dt") %>%
            arrange(dt) # Ensure sorted by time
        return(combined_df)
    } else {
        warning("No dataframes were generated.")
        return(tibble()) # Return empty tibble if no data
    }
}


#' Get Weather Forecast Data from Open-Meteo API
#'
#' Retrieves weather forecast data (future and/or recent past).
#'
#' @param forecast_days Integer. Number of future days (including today) to retrieve.
#' @param past_days Integer. Number of past days (relative to today) to retrieve.
#' @param variables Character vector. Hourly weather parameters to retrieve.
#' @param coordinates List of numeric vectors. Each inner vector is c(latitude, longitude).
#' @param ... Additional API parameters (passed as named arguments).
#'
#' @return A data frame (tibble) with datetime ('dt') and weather variables
#'         for each location, combined column-wise.
#'
#' @examples
#' \dontrun{
#' coords <- list(c(41.01, 28.98), c(39.93, 32.86)) # Istanbul, Ankara
#' vars <- c("temperature_2m", "shortwave_radiation")
#' forecast_data <- get_weather_forecast(7, 5, vars, coords, models = "ecmwf_ifs")
#' }
get_weather_forecast <- function(forecast_days, past_days, variables, coordinates, ...) {
    # API URL for forecast
    api_url <- "https://api.open-meteo.com/v1/forecast"

    all_dataframes <- list()
    additional_api_params <- list(...)

    # Loop through each coordinate pair
    for (i in seq_along(coordinates)) {
        coord <- coordinates[[i]]
        latitude <- coord[1]
        longitude <- coord[2]

        # Base parameters
        params <- list(
            latitude = latitude,
            longitude = longitude,
            forecast_days = forecast_days,
            past_days = past_days,
            hourly = paste(variables, collapse = ","), # API expects comma-separated string
            timezone = "Europe/Istanbul" # Explicitly set timezone
        )

        # Add any extra parameters provided via ...
        if (length(additional_api_params) > 0) {
            params <- c(params, additional_api_params)
        }
        # Special handling if 'models' is passed, needs to be comma-separated
        if ("models" %in% names(params) && is.vector(params$models)) {
            params$models <- paste(params$models, collapse = ",")
        }

        # Make the API request
        response <- GET(api_url, query = params)

        # Check for HTTP errors
        stop_for_status(response, task = paste("fetch forecast weather data for coord", i))

        # Parse the JSON response
        content <- content(response, "text", encoding = "UTF-8")
        data <- fromJSON(content, flatten = TRUE)

        if (!is.null(data$hourly) && length(data$hourly$time) > 0) {
            # Extract hourly data
            hourly_data <- as_tibble(data$hourly)

            # Convert time column to POSIXct (datetime)
            hourly_data$time <- ymd_hm(hourly_data$time, tz = "Europe/Istanbul") # Ensure correct TZ

            # Rename columns to match Python output format: location_XXX variable
            location_prefix <- paste0("location_", str_pad(i - 1, 3, pad = "0"), ".") # Python uses 0-based index
            names(hourly_data) <- case_when(
                names(hourly_data) == "time" ~ "dt",
                TRUE ~ paste0(location_prefix, names(hourly_data))
            )

            all_dataframes[[i]] <- hourly_data
        } else {
            warning(paste("No hourly forecast data returned for coordinate", i, "- Lat:", latitude, "Lon:", longitude))
        }
    }

    # Combine all data frames by the 'dt' column
    if (length(all_dataframes) > 0) {
        # Use reduce with full_join to merge all tibbles by 'dt'
        combined_df <- reduce(all_dataframes, full_join, by = "dt") %>%
            arrange(dt) # Ensure sorted by time
        return(combined_df)
    } else {
        warning("No forecast dataframes were generated.")
        return(tibble()) # Return empty tibble if no data
    }
}



get_production_data <- function(...) {
    # --- Load Production Data ---
    print("Loading production data...")
    # Construct the Google Sheet export URL (ensure sheet is shared 'anyone with link')
    gsheet_id <- "1IZsNp2TQdjYLQ_YwG3BtzwvutsDUM-G4" # Extracted from your URL
    production_url_csv <- paste0("https://docs.google.com/spreadsheets/d/", gsheet_id, "/export?format=csv")

    # Attempt to read the CSV
    production_data <- tryCatch(
        {
            read_csv(production_url_csv, show_col_types = FALSE) %>%
                select(dt, sun_rt) %>% # Select relevant columns
                # Parse datetime - **ASSUMPTION**: format is like 'YYYY-MM-DD HH:MM:SS' or similar
                # Adjust the parsing function/format if needed based on actual CSV content
                mutate(dt = parse_date_time(dt, orders = c("Ymd HMS", "Ymd HM", "Ymd"), quiet = TRUE)) %>%
                filter(!is.na(dt)) # Remove rows where date parsing failed
        },
        error = function(e) {
            warning(paste("Failed to read or process production data from URL:", production_url_csv, "\nError:", e$message))
            tibble(dt = POSIXct(), sun_rt = double()) # Return empty tibble on error
        }
    )
    return(production_data)
}
