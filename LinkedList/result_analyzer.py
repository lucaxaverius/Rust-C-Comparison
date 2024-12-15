import re
import numpy as np
import matplotlib.pyplot as plt
def process_log(log_data):
    # Regex patterns for extracting times
    insert_front_pattern = r"Time to insert \d+ elements at front: (\d+) ms"
    insert_back_pattern = r"Time to insert \d+ elements at back: (\d+) ms"
    remove_pattern = r"Time to remove all elements: (\d+) ms"

    # Extract times using regex
    insert_front_times = [int(m.group(1)) for m in re.finditer(insert_front_pattern, log_data)]
    insert_back_times = [int(m.group(1)) for m in re.finditer(insert_back_pattern, log_data)]
    remove_times = [int(m.group(1)) for m in re.finditer(remove_pattern, log_data)]

    # Organize remove_times into pairs for better interpretation
    remove_times_front = remove_times[0::2]  # Times for front insertions
    remove_times_back = remove_times[1::2]  # Times for back insertions

    # Print extracted data
    print("\nInsert Front Array:", insert_front_times)
    print("\nInsert Back Array:", insert_back_times)
    print("\nRemove Array:", remove_times)

    return insert_front_times, insert_back_times, remove_times, remove_times_front, remove_times_back

def plot_statistics(insert_front, insert_back, remove, remove_front, remove_back):
    # Calculate statistics
    datasets = {
        "Insert Front": insert_front,
        "Insert Back": insert_back,
        "Remove (Total)": remove,
        "Remove (Front)": remove_front,
        "Remove (Back)": remove_back,
    }
    
    stats = {name: (np.mean(data), np.min(data), np.max(data), np.std(data)) for name, data in datasets.items()}

    # Print statistics
    for name, (mean, min_val, max_val, std) in stats.items():
        print(f"\n{name} Statistics:")
        print(f"Mean: {mean:.2f} ms, Min: {min_val} ms, Max: {max_val} ms, Std Dev: {std:.2f} ms")

    # Plot graphs
    plt.figure(figsize=(12, 6))

    # Bar plot for means
    labels = list(stats.keys())
    means = [stats[name][0] for name in labels]
    mins = [stats[name][1] for name in labels]
    maxs = [stats[name][2] for name in labels]

    x = np.arange(len(labels))
    width = 0.3

    plt.bar(x - width, mins, width, label='Min')
    plt.bar(x, means, width, label='Mean')
    plt.bar(x + width, maxs, width, label='Max')

    plt.xlabel("Operation")
    plt.ylabel("Time (ms)")
    plt.title("Performance Metrics")
    plt.xticks(x, labels, rotation=45)
    plt.legend()
    plt.tight_layout()

    plt.show()

# Sample log data (replace with actual log content or read from file)
log_data = """
[12309.933557] C-List-Benchmark: The 1-th element is: 87628868
[12310.207491] C-List-Benchmark: Time to insert 10000000 elements at front: 273 ms
[12310.475735] C-List-Benchmark: Time to remove all elements: 268 ms
[12310.728458] C-List-Benchmark: Time to insert 10000000 elements at back: 252 ms
[12310.994485] C-List-Benchmark: Time to remove all elements: 266 ms
[12310.995329] C-List-Benchmark: Benchmark 1-th completed.
[12310.995331] C-List-Benchmark: Starting 2-th list_head benchmark module...
[12311.008776] C-List-Benchmark: The 1-th element is: 89293393
[12311.259781] C-List-Benchmark: Time to insert 10000000 elements at front: 250 ms
[12311.526213] C-List-Benchmark: Time to remove all elements: 266 ms
[12311.779683] C-List-Benchmark: Time to insert 10000000 elements at back: 253 ms
[12312.041982] C-List-Benchmark: Time to remove all elements: 262 ms
[12312.042885] C-List-Benchmark: Benchmark 2-th completed.
[12312.042887] C-List-Benchmark: Starting 3-th list_head benchmark module...
[12312.057359] C-List-Benchmark: The 1-th element is: 90957918
[12312.309501] C-List-Benchmark: Time to insert 10000000 elements at front: 252 ms
[12312.579545] C-List-Benchmark: Time to remove all elements: 270 ms
[12312.831718] C-List-Benchmark: Time to insert 10000000 elements at back: 252 ms
[12313.090984] C-List-Benchmark: Time to remove all elements: 259 ms
[12313.091964] C-List-Benchmark: Benchmark 3-th completed.
[12313.091966] C-List-Benchmark: Starting 4-th list_head benchmark module...
[12313.105836] C-List-Benchmark: The 1-th element is: 92622443
[12313.357134] C-List-Benchmark: Time to insert 10000000 elements at front: 251 ms
[12313.624521] C-List-Benchmark: Time to remove all elements: 267 ms
[12313.878560] C-List-Benchmark: Time to insert 10000000 elements at back: 254 ms
[12314.140109] C-List-Benchmark: Time to remove all elements: 261 ms
[12314.140885] C-List-Benchmark: Benchmark 4-th completed.
[12314.140887] C-List-Benchmark: Starting 5-th list_head benchmark module...
[12314.156594] C-List-Benchmark: The 1-th element is: 94286968
[12314.406523] C-List-Benchmark: Time to insert 10000000 elements at front: 249 ms
[12314.671795] C-List-Benchmark: Time to remove all elements: 265 ms
[12314.923919] C-List-Benchmark: Time to insert 10000000 elements at back: 252 ms
[12315.185212] C-List-Benchmark: Time to remove all elements: 261 ms
[12315.185979] C-List-Benchmark: Benchmark 5-th completed.
[12315.185981] C-List-Benchmark: Starting 6-th list_head benchmark module...
[12315.199842] C-List-Benchmark: The 1-th element is: 95951493
[12315.448753] C-List-Benchmark: Time to insert 10000000 elements at front: 248 ms
[12315.714103] C-List-Benchmark: Time to remove all elements: 265 ms
[12315.965340] C-List-Benchmark: Time to insert 10000000 elements at back: 251 ms
[12316.227062] C-List-Benchmark: Time to remove all elements: 261 ms
[12316.227830] C-List-Benchmark: Benchmark 6-th completed.
[12316.227832] C-List-Benchmark: Starting 7-th list_head benchmark module...
[12316.241322] C-List-Benchmark: The 1-th element is: 97616018
[12316.489070] C-List-Benchmark: Time to insert 10000000 elements at front: 247 ms
[12316.750935] C-List-Benchmark: Time to remove all elements: 261 ms
[12317.005498] C-List-Benchmark: Time to insert 10000000 elements at back: 254 ms
[12317.290178] C-List-Benchmark: Time to remove all elements: 284 ms
[12317.292235] C-List-Benchmark: Benchmark 7-th completed.
[12317.292244] C-List-Benchmark: Starting 8-th list_head benchmark module...
[12317.316617] C-List-Benchmark: The 1-th element is: 99280543
[12317.899222] C-List-Benchmark: Time to insert 10000000 elements at front: 582 ms
[12318.203246] C-List-Benchmark: Time to remove all elements: 304 ms
[12318.466061] C-List-Benchmark: Time to insert 10000000 elements at back: 262 ms
[12318.727132] C-List-Benchmark: Time to remove all elements: 261 ms
[12318.728102] C-List-Benchmark: Benchmark 8-th completed.
[12318.728104] C-List-Benchmark: Starting 9-th list_head benchmark module...
[12318.741875] C-List-Benchmark: The 1-th element is: 100945068
[12319.003140] C-List-Benchmark: Time to insert 10000000 elements at front: 261 ms
[12319.325456] C-List-Benchmark: Time to remove all elements: 322 ms
[12319.583658] C-List-Benchmark: Time to insert 10000000 elements at back: 258 ms
[12319.842141] C-List-Benchmark: Time to remove all elements: 258 ms
[12319.843178] C-List-Benchmark: Benchmark 9-th completed.
[12319.843182] C-List-Benchmark: Starting 10-th list_head benchmark module...
[12319.857348] C-List-Benchmark: The 1-th element is: 102609593
[12320.114765] C-List-Benchmark: Time to insert 10000000 elements at front: 257 ms
[12320.380415] C-List-Benchmark: Time to remove all elements: 265 ms
[12320.635884] C-List-Benchmark: Time to insert 10000000 elements at back: 255 ms
[12320.898488] C-List-Benchmark: Time to remove all elements: 262 ms
[12320.899496] C-List-Benchmark: Benchmark 10-th completed.
[12320.899498] C-List-Benchmark: Starting 11-th list_head benchmark module...
[12320.913298] C-List-Benchmark: The 1-th element is: 104274118
[12321.165570] C-List-Benchmark: Time to insert 10000000 elements at front: 252 ms
[12321.430589] C-List-Benchmark: Time to remove all elements: 265 ms
[12321.688621] C-List-Benchmark: Time to insert 10000000 elements at back: 258 ms
[12321.942733] C-List-Benchmark: Time to remove all elements: 254 ms
[12321.943769] C-List-Benchmark: Benchmark 11-th completed.
[12321.943771] C-List-Benchmark: Starting 12-th list_head benchmark module...
[12321.956635] C-List-Benchmark: The 1-th element is: 105938643
[12322.206446] C-List-Benchmark: Time to insert 10000000 elements at front: 249 ms
[12322.473645] C-List-Benchmark: Time to remove all elements: 267 ms
[12322.727448] C-List-Benchmark: Time to insert 10000000 elements at back: 253 ms
[12322.985630] C-List-Benchmark: Time to remove all elements: 258 ms
[12322.986406] C-List-Benchmark: Benchmark 12-th completed.
[12322.986407] C-List-Benchmark: Starting 13-th list_head benchmark module...
[12323.000733] C-List-Benchmark: The 1-th element is: 107603168
[12323.248197] C-List-Benchmark: Time to insert 10000000 elements at front: 247 ms
[12323.508788] C-List-Benchmark: Time to remove all elements: 260 ms
[12323.759077] C-List-Benchmark: Time to insert 10000000 elements at back: 250 ms
[12324.018485] C-List-Benchmark: Time to remove all elements: 259 ms
[12324.019403] C-List-Benchmark: Benchmark 13-th completed.
[12324.019412] C-List-Benchmark: Starting 14-th list_head benchmark module...
[12324.033428] C-List-Benchmark: The 1-th element is: 109267693
[12324.290304] C-List-Benchmark: Time to insert 10000000 elements at front: 256 ms
[12324.555764] C-List-Benchmark: Time to remove all elements: 265 ms
[12324.809638] C-List-Benchmark: Time to insert 10000000 elements at back: 253 ms
[12325.067239] C-List-Benchmark: Time to remove all elements: 257 ms
[12325.068143] C-List-Benchmark: Benchmark 14-th completed.
[12325.068145] C-List-Benchmark: Starting 15-th list_head benchmark module...
[12325.081607] C-List-Benchmark: The 1-th element is: 110932218
[12325.332365] C-List-Benchmark: Time to insert 10000000 elements at front: 250 ms
[12325.597461] C-List-Benchmark: Time to remove all elements: 265 ms
[12325.858350] C-List-Benchmark: Time to insert 10000000 elements at back: 260 ms
[12326.120406] C-List-Benchmark: Time to remove all elements: 262 ms
[12326.121384] C-List-Benchmark: Benchmark 15-th completed.
[12326.121387] C-List-Benchmark: Starting 16-th list_head benchmark module...
[12326.136238] C-List-Benchmark: The 1-th element is: 112596743
[12326.392329] C-List-Benchmark: Time to insert 10000000 elements at front: 256 ms
[12326.656954] C-List-Benchmark: Time to remove all elements: 264 ms
[12326.918575] C-List-Benchmark: Time to insert 10000000 elements at back: 261 ms
[12327.181176] C-List-Benchmark: Time to remove all elements: 262 ms
[12327.181951] C-List-Benchmark: Benchmark 16-th completed.
[12327.181953] C-List-Benchmark: Starting 17-th list_head benchmark module...
[12327.195898] C-List-Benchmark: The 1-th element is: 114261268
[12327.457056] C-List-Benchmark: Time to insert 10000000 elements at front: 261 ms
[12327.723948] C-List-Benchmark: Time to remove all elements: 266 ms
[12327.985700] C-List-Benchmark: Time to insert 10000000 elements at back: 261 ms
[12328.250039] C-List-Benchmark: Time to remove all elements: 264 ms
[12328.251234] C-List-Benchmark: Benchmark 17-th completed.
[12328.251236] C-List-Benchmark: Starting 18-th list_head benchmark module...
[12328.264684] C-List-Benchmark: The 1-th element is: 115925793
[12328.523264] C-List-Benchmark: Time to insert 10000000 elements at front: 258 ms
[12328.789081] C-List-Benchmark: Time to remove all elements: 265 ms
[12329.052882] C-List-Benchmark: Time to insert 10000000 elements at back: 263 ms
[12329.318107] C-List-Benchmark: Time to remove all elements: 265 ms
[12329.319181] C-List-Benchmark: Benchmark 18-th completed.
[12329.319183] C-List-Benchmark: Starting 19-th list_head benchmark module...
[12329.332634] C-List-Benchmark: The 1-th element is: 117590318
[12329.589803] C-List-Benchmark: Time to insert 10000000 elements at front: 257 ms
[12329.856062] C-List-Benchmark: Time to remove all elements: 266 ms
[12330.116830] C-List-Benchmark: Time to insert 10000000 elements at back: 260 ms
[12330.383578] C-List-Benchmark: Time to remove all elements: 266 ms
[12330.384516] C-List-Benchmark: Benchmark 19-th completed.
[12330.384518] C-List-Benchmark: Starting 20-th list_head benchmark module...
[12330.398121] C-List-Benchmark: The 1-th element is: 119254843
[12330.657880] C-List-Benchmark: Time to insert 10000000 elements at front: 259 ms
[12330.923026] C-List-Benchmark: Time to remove all elements: 265 ms
[12331.177124] C-List-Benchmark: Time to insert 10000000 elements at back: 254 ms
[12331.435118] C-List-Benchmark: Time to remove all elements: 257 ms
[12331.435975] C-List-Benchmark: Benchmark 20-th completed.
[12331.435977] C-List-Benchmark: Starting 21-th list_head benchmark module...
[12331.451155] C-List-Benchmark: The 1-th element is: 120919368
[12331.699074] C-List-Benchmark: Time to insert 10000000 elements at front: 247 ms
[12331.965123] C-List-Benchmark: Time to remove all elements: 266 ms
[12332.218755] C-List-Benchmark: Time to insert 10000000 elements at back: 253 ms
[12332.480436] C-List-Benchmark: Time to remove all elements: 261 ms
[12332.481353] C-List-Benchmark: Benchmark 21-th completed.
[12332.481354] C-List-Benchmark: Starting 22-th list_head benchmark module...
[12332.494824] C-List-Benchmark: The 1-th element is: 122583893
[12332.746751] C-List-Benchmark: Time to insert 10000000 elements at front: 251 ms
[12333.007955] C-List-Benchmark: Time to remove all elements: 261 ms
[12333.264429] C-List-Benchmark: Time to insert 10000000 elements at back: 256 ms
[12333.530650] C-List-Benchmark: Time to remove all elements: 266 ms
[12333.531642] C-List-Benchmark: Benchmark 22-th completed.
[12333.531643] C-List-Benchmark: Starting 23-th list_head benchmark module...
[12333.545863] C-List-Benchmark: The 1-th element is: 124248418
[12333.805418] C-List-Benchmark: Time to insert 10000000 elements at front: 259 ms
[12334.074102] C-List-Benchmark: Time to remove all elements: 268 ms
[12334.335761] C-List-Benchmark: Time to insert 10000000 elements at back: 261 ms
[12334.596952] C-List-Benchmark: Time to remove all elements: 261 ms
[12334.597927] C-List-Benchmark: Benchmark 23-th completed.
[12334.597929] C-List-Benchmark: Starting 24-th list_head benchmark module...
[12334.611882] C-List-Benchmark: The 1-th element is: 125912943
[12334.870547] C-List-Benchmark: Time to insert 10000000 elements at front: 258 ms
[12335.140892] C-List-Benchmark: Time to remove all elements: 270 ms
[12335.412203] C-List-Benchmark: Time to insert 10000000 elements at back: 271 ms
[12335.675482] C-List-Benchmark: Time to remove all elements: 263 ms
[12335.676773] C-List-Benchmark: Benchmark 24-th completed.
[12335.676780] C-List-Benchmark: Starting 25-th list_head benchmark module...
[12335.691256] C-List-Benchmark: The 1-th element is: 127577468
[12335.955907] C-List-Benchmark: Time to insert 10000000 elements at front: 264 ms
[12336.223162] C-List-Benchmark: Time to remove all elements: 267 ms
[12336.486270] C-List-Benchmark: Time to insert 10000000 elements at back: 263 ms
[12336.754055] C-List-Benchmark: Time to remove all elements: 267 ms
[12336.755190] C-List-Benchmark: Benchmark 25-th completed.
[12336.755192] C-List-Benchmark: Starting 26-th list_head benchmark module...
[12336.770901] C-List-Benchmark: The 1-th element is: 129241993
[12337.025227] C-List-Benchmark: Time to insert 10000000 elements at front: 254 ms
[12337.295852] C-List-Benchmark: Time to remove all elements: 270 ms
[12337.553060] C-List-Benchmark: Time to insert 10000000 elements at back: 257 ms
[12337.817808] C-List-Benchmark: Time to remove all elements: 264 ms
[12337.818697] C-List-Benchmark: Benchmark 26-th completed.
[12337.818699] C-List-Benchmark: Starting 27-th list_head benchmark module...
[12337.832481] C-List-Benchmark: The 1-th element is: 130906518
[12338.088605] C-List-Benchmark: Time to insert 10000000 elements at front: 256 ms
[12338.356809] C-List-Benchmark: Time to remove all elements: 268 ms
[12338.616500] C-List-Benchmark: Time to insert 10000000 elements at back: 259 ms
[12338.884538] C-List-Benchmark: Time to remove all elements: 268 ms
[12338.885334] C-List-Benchmark: Benchmark 27-th completed.
[12338.885335] C-List-Benchmark: Starting 28-th list_head benchmark module...
[12338.900016] C-List-Benchmark: The 1-th element is: 132571043
[12339.155134] C-List-Benchmark: Time to insert 10000000 elements at front: 255 ms
[12339.428211] C-List-Benchmark: Time to remove all elements: 273 ms
[12339.685633] C-List-Benchmark: Time to insert 10000000 elements at back: 257 ms
[12339.951140] C-List-Benchmark: Time to remove all elements: 265 ms
[12339.951980] C-List-Benchmark: Benchmark 28-th completed.
[12339.951981] C-List-Benchmark: Starting 29-th list_head benchmark module...
[12339.965206] C-List-Benchmark: The 1-th element is: 134235568
[12340.218088] C-List-Benchmark: Time to insert 10000000 elements at front: 252 ms
[12340.491456] C-List-Benchmark: Time to remove all elements: 273 ms
[12340.751963] C-List-Benchmark: Time to insert 10000000 elements at back: 260 ms
[12341.025035] C-List-Benchmark: Time to remove all elements: 273 ms
[12341.026039] C-List-Benchmark: Benchmark 29-th completed.
[12341.026055] C-List-Benchmark: Starting 30-th list_head benchmark module...
[12341.039727] C-List-Benchmark: The 1-th element is: 135900093
[12341.298385] C-List-Benchmark: Time to insert 10000000 elements at front: 258 ms
[12341.562141] C-List-Benchmark: Time to remove all elements: 263 ms
[12341.819610] C-List-Benchmark: Time to insert 10000000 elements at back: 257 ms
[12342.082636] C-List-Benchmark: Time to remove all elements: 263 ms
[12342.083493] C-List-Benchmark: Benchmark 30-th completed.
"""

# Process the log and get arrays
insert_front, insert_back, remove, remove_front, remove_back = process_log(log_data)

# Plot statistics
plot_statistics(insert_front, insert_back, remove, remove_front, remove_back)
