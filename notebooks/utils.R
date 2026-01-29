# Utility functions for R data analysis and logging

# =============================================================================
# Logging Functions
# =============================================================================

# Global log file connection (set by set_log_file)
.log_file <- NULL

#' Set the global log file for log_and_print to use
#'
#' @param log_path Character string, path to log file
#' @return The log file connection (invisibly)
#' @export
set_log_file <- function(log_path) {
  # Close existing log file if open
  if (!is.null(.log_file)) {
    close(.log_file)
  }
  # Create log directory if needed
  log_dir <- dirname(log_path)
  if (log_dir != "." && !dir.exists(log_dir)) {
    dir.create(log_dir, showWarnings = FALSE, recursive = TRUE)
  }
  # Open new log file
  .log_file <<- file(log_path, "w")
  cat("Logging to:", log_path, "\n")
  return(invisible(.log_file))
}

#' Log and print message (writes to both log file and console)
#'
#' Similar to Python's log_and_print function. Accepts sprintf-style formatting.
#'
#' @param fmt Character string with format specifiers (like sprintf)
#' @param ... Additional arguments to be passed to sprintf for formatting
#' @export
log_and_print <- function(fmt, ...) {
  # Format message using sprintf if additional arguments provided
  if (length(list(...)) > 0) {
    message <- sprintf(fmt, ...)
  } else {
    message <- fmt
  }
  
  # Write to log file if it's open
  if (!is.null(.log_file) && isOpen(.log_file)) {
    writeLines(message, .log_file)
    flush(.log_file)
  }
  # Print to console
  cat(message, "\n")
}

#' Log message to file only (no console output)
#'
#' Similar to log_and_print but only writes to log file, not console.
#' Useful for verbose initialization messages that shouldn't clutter console output.
#'
#' @param fmt Character string with format specifiers (like sprintf)
#' @param ... Additional arguments to be passed to sprintf for formatting
#' @export
log_only <- function(fmt, ...) {
  # Format message using sprintf if additional arguments provided
  if (length(list(...)) > 0) {
    message <- sprintf(fmt, ...)
  } else {
    message <- fmt
  }
  
  # Write to log file if it's open (but don't print to console)
  if (!is.null(.log_file) && isOpen(.log_file)) {
    writeLines(message, .log_file)
    flush(.log_file)
  }
}

#' Close log file (call at end of notebook or in cleanup)
#'
#' @export
close_log_file <- function() {
  if (!is.null(.log_file) && isOpen(.log_file)) {
    close(.log_file)
    .log_file <<- NULL
    cat("Log file closed.\n")
  }
}

#' Initialize logging with header
#'
#' Sets up logging and writes a standard header to the log file.
#' This is a convenience function that combines set_log_file with header logging.
#'
#' @param log_path Character string, path to log file
#' @param title Character string, title for the log header
#' @export
init_logging <- function(log_path, title = "ANALYSIS") {
  set_log_file(log_path)
  log_only(paste0(rep("=", 80), collapse = ""))
  log_only(title)
  log_only(paste0(rep("=", 80), collapse = ""))
  log_only(paste("Timestamp:", Sys.time()))
  log_only(paste0(rep("=", 80), collapse = ""))
}

