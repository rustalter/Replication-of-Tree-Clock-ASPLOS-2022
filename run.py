import os
import sys
import optparse
import subprocess
import zipfile
import pandas as pd
from statistics import mean



def initialize_csv(filename):
    if not os.path.isfile(filename):
        with open(filename, 'w') as f:
            f.write('benchmark,algorithm,num_iter,individual_runs,average_total_time\n')


def export_results(trace, analyses, results):
    filename = os.path.join(result_path, analyses + "_result.csv")
    initialize_csv(filename)

    with open(filename, 'a') as f:
        for a, v in results.items():
            f.write("{},{},{},{},{}\n".format(trace, a, len(v), ' - '.join(str(x) for x in v), mean(v)))


def execute_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    (output, err) = p.communicate()
    p_status = p.wait()
    return output


def run(algorithm, benchmark, memory):
    memory_option = "-Xmx{}m -Xms{}m ".format(memory, memory)
    cmd = "java {} -cp {} {} -f=std -p={}".format(memory_option, rapid_path, algorithm, benchmark)
    print(cmd)
    return execute_cmd(cmd).decode('utf-8')


def replicate_results(traces, compared_analyses, memory, num_iter=1):
    was_zipped_flag = False
    for t in traces:
        if os.path.splitext(t)[1] == ".zip":
            with zipfile.ZipFile(t, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(t))
                t = os.path.join(os.path.dirname(t), zip_ref.namelist()[0])
                was_zipped_flag = True

        for c in compared_analyses:
            print("Comparing the analyses: {}".format(c))

            algs = analyses_2main_classes_map[c]
            results = {a: [] for a in algs}

            for i in range(0, num_iter):
                for a in algs:
                    print("iteration: {}/{}, benchmark: {}, algorithm: {}".format(i+1, num_iter, t, a))

                    output = run(a, t, memory)
                    print(output)
                    print("\n")

                    results[a].append(int(output.split("Time for analysis = ")[1].split()[0]))

            print("-----------------\n\n\n")

            export_results(t, c, results)

        if was_zipped_flag:
            os.remove(t)



def get_analyses(included_analyses):
    analyses = []
    if included_analyses == "all":
        analyses = list(analyses_2main_classes_map.keys())
    else:
        analyses = included_analyses.split(',')
        for a in analyses:
            if a not in analyses_2main_classes_map:
                print("Provided unknown analyses: {}! Exiting.".format(a))
                sys.exit()
    return analyses


def get_traces(benchmarks_path, included_traces):
    benchmarks_csv_path = os.path.join(benchmarks_path, "benchmarks.csv")
    df = pd.read_csv(benchmarks_csv_path)
    traces = []
    if included_traces == "small":
        traces = df[df["category"] == "small"]["name"].values
    elif included_traces == "all":
        traces = df["name"].values

    traces = [os.path.join(benchmarks_path, trace_path) for trace_path in traces]
    archive_files = []
    for t in traces:
        if os.path.isdir(t):
            files = os.listdir(t)
            extensions = [".zip"]

            archive_file = [os.path.join(benchmarks_path, t, f) for f in files \
                                if os.path.splitext(os.path.join(benchmarks_path, t, f))[1] in extensions][0]
            archive_files.append(archive_file)
            print("Found the benchmark: {}.\n".format(t))
        else:
            print("Cannot find the benchmark: {}. Skipping it.\n".format(t))

    return archive_files


def create_paths(ae_path, result_folder_name=None):
    rapid_path = os.path.join(ae_path, "rapid", "rapid-tree-clocks.jar")

    benchmarks_path = os.path.join(ae_path, "benchmarks")

    if result_folder_name is None:
        result_path = os.path.join(ae_path, "results")
    else:
        result_path = os.path.join(ae_path, "results", result_folder_name)


    return rapid_path, benchmarks_path, result_path


def get_analyses_2main_classes_map():
    map = \
            {
                "HB":              ["HBVectorClockNoRace",        "HBTreeClockNoRace"], 
                "HBRaceAnalysis":  ["HBVectorClockRaceAnalysis",  "HBTreeClockRaceAnalysis"],
                "SHB":             ["SHBVectorClockNoRace",       "SHBTreeClockNoRace"], 
                "SHBRaceAnalysis": ["SHBVectorClockRaceAnalysis", "SHBTreeClockRaceAnalysis"],
                "MAZ":             ["MAZVectorClockNoRace",       "MAZTreeClockNoRace"], 
                "MAZRaceAnalysis": ["MAZVectorClockRaceAnalysis", "MAZTreeClockRaceAnalysis"]
            }
    return map


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b", "--benchmarks", dest="benchmarks", default="all", 
                        help="run the script on the selected group of benchmarks: small, all \
                            (Defaul: all). This option is mutually exclusive with -p.")
    parser.add_option("-p", "--trace-path", dest="trace_path", default=None, 
                        help="run the script on an individual trace. This option is mutually exclusive with -b.")
    parser.add_option("-i", "--iterations", dest="iters", default=1, type="int",
                        help="the number of times each analyses will be repeated (Default: 1).")
    parser.add_option("-m", "--heap-memory-size", dest="memory", default=320, help="JVM heap size in MB (Default: 30000)")
    parser.add_option("-a","--analyses", dest="analyses", default="all",
                        help="run a subset of the available analyses: \
                            HB,HBRaceAnalysis,SHB,SHBRaceAnalysis,MAZ,MAZRaceAnalysis or all (Default: all).")
    parser.add_option("-n", "--results-folder-name", dest="result_folder_name", default=None, 
                        help="name of the folder under $AE_HOME/results to which the resulting .csv files will be extracted.")
    (options, args) = parser.parse_args()


    if os.getenv("AE_HOME") is None:
        print("Please set the environment variable AE_HOME.")
        sys.exit()
    else:
        rapid_path, benchmarks_path, result_path = create_paths(os.getenv("AE_HOME"), options.result_folder_name)
        if options.trace_path is None:
            traces = get_traces(benchmarks_path, options.benchmarks)
        else: 
            traces = [options.trace_path]

        analyses_2main_classes_map = get_analyses_2main_classes_map()
        analyses = get_analyses(options.analyses)

        replicate_results(traces, analyses, options.memory, num_iter=options.iters)
