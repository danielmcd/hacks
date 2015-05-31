import numpy
import matplotlib.pyplot as plt
from nupic.algorithms.anomaly import computeRawAnomalyScore
from encoder.encoder import Encoder, TrainerFile
from encoder.utils.utils import print_err

class Decoder(object):
    '''
    Given a TP model, predict the anomaly score for a set of stock data points.
    @param encoder: an Encoder object holding a trained temporal pooler instance
    '''
    def __init__(self, encoder):
    	self.encoder = encoder
	self.tp = encoder.tp

    def run_decoder(self, stock_records):
    	'''
	Run the stock records through the TP without learning.
	compute the inference at each step and the anomaly score.
	@param stock_records: list type of StockRecord objects
	@return the average the anomaly score for the sequence.
	'''
	# See https://github.com/numenta/nupic/wiki/Anomaly-Detection-and-Anomaly-Scores
    	data_encoder = self.encoder._get_encoder()
        input_array = numpy.zeros(encoder.width, dtype="int32")

        self.tp.reset()

	previous_predicted_columns = None
	scores = []
        for i, record in enumerate(stock_records):
            input_array[:] = numpy.concatenate(data_encoder.encodeEachField(record))
            self.tp.compute(input_array, enableLearn=False, computeInfOutput=True)
	    active_columns = set(tp.getActiveState().max(axis=1).nonzero()[0].flat)
	    predicted_columns = set(tp.getPredictedState().max(axis=1).nonzero()[0].flat)
	    if previous_predicted_columns is not None:
		score.append(computeRawAnomalyScore(active_columns,  previous_predicted_columns))
	    previous_predicted_columns = predicted_columns

	return numpy.mean(scores)


def print_usage_and_exit():
    print_err("\n" + sys.argv[0] + " <test_datasets_path>")
    print_err("\ntest_datasets_path\tpath for the test datasets")
    exit(1)


class EventScore(object):
    def __init__(self, index, score):
    	self.index = index
	self.score = score


class Tester(object):
    def __init__(self, test_datasets_file):
    	self.test_datasets_file = test_datasets_file

    def calculate_anomaly_scores():
    	trainer_file = TrainerFile(test_datasets_file)
	test_datasets = trainer_file.get_encoded_data()
	encoder = Encoder(False)  # Create the Encoder (load TP)
	decoder = Decoder(encoder)  # Create the Decoder

	# Calculate the anomaly score for each event in the test set
	event_scores = []
	for i, dataset in enumerate(test_datasets):
	    score = decoder.run_decoder(dataset)
	    event_scores.append(EventScore(i, score))
	
	return event_scores


class EventScoreGraph(object):
    def __init__(self, event_scores):
    	self.event_scores = event_scores

    def display(self):
    	pareto = sorted(event_scores, lambda e: e.score)
	pareto_indices = range(len(pareto))
	pareto_scores = [e.score for e in pareto]
        plt.plot(pareto_indices, pareto_scores, label="Pareto of Avg Anomaly for Test Events")


def check_command_line_args():
    if len(sys.argv) < 2:
        print_usage_and_exit()
    if not os.path.isfile(sys.argv[1]):
        print_err("ERROR: " + sys.argv[1] + " is not a file")
        print_usage_and_exit()
    return sys.argv[1]


if __name__ == "__main__":
    test_datasets_path = check_command_line_args()
    event_scores = Tester(test_datasets_path).calculate_anomaly_scores()
    # Produce a pareto diagram of anomaly score vs. event
    EventScoreGraph(event_scores).display()

