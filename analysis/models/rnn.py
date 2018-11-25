import numpy as np
import tensorflow as tf

class RNN():
    def __init__(self, embeddings, num_classes, hidden_size, max_len=32, learning_rate=0.001):
        self.embeddings = embeddings
        self.num_classes = num_classes
        self.hidden_size = hidden_size
        self.max_len = max_len
        self.learning_rate = learning_rate
        self.create_inputs()
        self.create_graph()

    def create_inputs(self):
        self.X = tf.placeholder(dtype=tf.float32, name="X", shape=[None, self.max_len, self.embeddings.vector_size])
        self.Y = tf.placeholder(dtype=tf.int64, name="Y", shape=[None])
        self.keep_prob = tf.placeholder_with_default(1., shape=[], name="keep_prob")

    def create_graph(self):
        rnn_outputs, _ = tf.nn.bidirectional_dynamic_rnn(
                                tf.nn.rnn_cell.BasicLSTMCell(self.hidden_size),
                                tf.nn.rnn_cell.BasicLSTMCell(self.hidden_size),
                                inputs=self.X, dtype=tf.float32)

        fw_outputs, bw_outputs = rnn_outputs

        W = tf.Variable(tf.random_normal([self.hidden_size], stddev=0.1))
        H = fw_outputs + bw_outputs  # (batch_size, seq_len, HIDDEN_SIZE)
        M = tf.tanh(H)
        self.shp = tf.shape(M)

        self.alpha = tf.nn.softmax(tf.reshape(tf.matmul(tf.reshape(M, [-1, self.hidden_size]),
                                                        tf.reshape(W, [-1, 1]), name="get_attn_logits"),
                                              (-1, self.max_len)))  # batch_size x seq_len
        r = tf.matmul(tf.transpose(H, [0, 2, 1]),
                      tf.reshape(self.alpha, [-1, self.max_len, 1]), name="aggregate_attn")
        r = tf.squeeze(r, axis=-1)
        h_star = tf.tanh(r)  # (batch , HIDDEN_SIZE)

        h_drop = tf.nn.dropout(h_star, self.keep_prob)

        # Fully connected layer（dense layer)
        FC_W = tf.Variable(tf.truncated_normal([self.hidden_size, self.num_classes], stddev=0.1))
        FC_b = tf.Variable(tf.constant(0., shape=[self.num_classes]))
        logits = tf.nn.xw_plus_b(h_drop, FC_W, FC_b)
        self.logits = logits

        loss = tf.reduce_mean(
            tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=self.Y))
        tf.summary.scalar("loss", loss)

        # prediction
        predictions = tf.argmax(logits, 1)
        self.predictions = predictions
        self.accuracy = tf.reduce_mean(tf.cast(tf.equal(self.Y, predictions), tf.float32))
        tf.summary.scalar("accuracy", self.accuracy)

        # optimization
        loss_to_minimize = loss
        tvars = tf.trainable_variables()
        gradients = tf.gradients(loss_to_minimize, tvars, aggregation_method=tf.AggregationMethod.EXPERIMENTAL_TREE)
        grads, global_norm = tf.clip_by_global_norm(gradients, 1.0)

        self.global_step = tf.Variable(0, name="global_step", trainable=False)
        opt = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        self.train_op = opt.apply_gradients(zip(grads, tvars), global_step=self.global_step,
                                            name='train_step')
        self.merged_summary = tf.summary.merge_all()

