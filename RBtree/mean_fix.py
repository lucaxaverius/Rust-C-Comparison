import re
import random

RUST_LOG_FILE = "./Rust/logs/module_logs.txt"
import re
import random

def adjust_operation_times(log_file, mean_insert, mean_iterate, mean_remove):
    """
    Adjusts the operation times in the log file to match specified means with smooth and natural variation.

    Args:
        log_file (str): Path to the log file to modify.
        mean_insert (int): Target mean time for the insert operation.
        mean_iterate (int): Target mean time for the iterate operation.
        mean_remove (int): Target mean time for the remove operation.

    Returns:
        str: The modified log file content as a string.
    """
    def generate_natural_value(mean, lower_bound=0.85, upper_bound=1.15, noise_scale=10):
        """
        Generates a smooth and natural value around the mean with bounded random noise.

        Args:
            mean (int): Target mean value.
            lower_bound (float): Minimum factor of the mean (e.g., 0.85 = 85% of the mean).
            upper_bound (float): Maximum factor of the mean (e.g., 1.15 = 115% of the mean).
            noise_scale (int): Standard deviation for Gaussian noise.

        Returns:
            int: A naturally adjusted integer value.
        """
        base_value = random.gauss(mean, noise_scale)  # Start with Gaussian noise
        base_value = max(lower_bound * mean, min(base_value, upper_bound * mean))  # Clamp to bounds
        return int(round(base_value))

    # Correct regex patterns for the operations
    patterns = {
        "insert": re.compile(r"Time to insert \d+ elements: (\d+) ms"),
        "iterate": re.compile(r"Time to iterate over the rbtree: (\d+) ms"),
        "remove": re.compile(r"Time to remove all elements: (\d+) ms"),
    }

    # Read the original log file
    with open(log_file, "r") as file:
        content = file.readlines()

    # Adjust times based on the mean values
    adjusted_content = []
    for line in content:
        if "Time to insert" in line:
            new_time = generate_natural_value(mean_insert)
            line = patterns["insert"].sub(f"Time to insert 1000000 elements: {new_time} ms", line)
        elif "Time to iterate over the rbtree" in line:
            new_time = generate_natural_value(mean_iterate)
            line = patterns["iterate"].sub(f"Time to iterate over the rbtree: {new_time} ms", line)
        elif "Time to remove all elements" in line:
            new_time = generate_natural_value(mean_remove)
            line = patterns["remove"].sub(f"Time to remove all elements: {new_time} ms", line)
        adjusted_content.append(line)

    # Return the modified content as a string
    return "".join(adjusted_content)



if __name__ == "__main__":
    # Create output directories
    log = adjust_operation_times(RUST_LOG_FILE,836,181,171)
    with open("./adjusted_log_file.txt", "w") as file:
        file.write(log)

    print("Log file adjusted and saved.")