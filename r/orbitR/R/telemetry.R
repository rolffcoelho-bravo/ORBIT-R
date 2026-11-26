#' Read original OPS-SAT measured segments
#'
#' @param path File path to original `segments.csv` from Zenodo record 12588359.
#' @param check Verify the pinned publisher MD5 before reading (default TRUE).
#' @return A data.frame of original measured samples.
#' @export
read_opssat_segments <- function(path, check = TRUE) {
  if (!file.exists(path)) stop("Raw OPS-SAT measurements not available")
  if (check) {
    actual <- unname(tools::md5sum(path))
    if (is.na(actual) || tolower(actual) != "1f4b6ffd0359efac96a6698ff557e0f9")
      stop("Pinned source checksum mismatch")
  }
  x <- utils::read.csv(path, stringsAsFactors = FALSE)
  required <- c("timestamp", "channel", "value", "label", "segment", "sampling", "train")
  if (!all(required %in% names(x))) stop("Wrong original telemetry schema")
  if (!is.numeric(x$value) || any(!is.finite(x$value))) stop("Nonfinite or invalid source observation")
  x
}
#' Summarize original measurements from one segment
#'
#' @param data Data frame from `read_opssat_segments`.
#' @param channel Channel name.
#' @param segment Original segment identifier.
#' @return Named list of basic measured statistics.
#' @export
segment_summary <- function(data, channel, segment) {
  x <- data[data$channel == channel & as.character(data$segment) == as.character(segment), , drop=FALSE]
  if (nrow(x) < 3L) stop("Insufficient actual observations")
  y <- as.numeric(x$value)
  list(channel = channel, segment = as.character(segment), observations = length(y),
       median = stats::median(y), standard_deviation = stats::sd(y),
       minimum = min(y), maximum = max(y))
}
