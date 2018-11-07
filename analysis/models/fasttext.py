import tensorflow as tf 

class FastText():
    def __init__(self, vocab, num_classes, regularize_coef=0, learning_rate=0.001, embedding_dim=10):
        self.vocab = vocab
        self.num_classes = num_classes
        self.regularize_coef = regularize_coef
        self.learning_rate = learning_rate
        self.embedding_dim = embedding_dim
        self.create_inputs()
        self.create_graph()

    def create_inputs(self):
        # X is a 1D array of sentences as space-separated strings
        self.X = tf.placeholder(dtype=tf.string, name="X", shape=[None])
        self.Y = tf.placeholder(dtype=tf.int32, name="Y", shape=[None])

    def create_graph(self):
        sparse_text = tf.string_split(self.X, delimiter=" ")

        table = tf.contrib.lookup.index_table_from_tensor(mapping=tf.constant(self.vocab), num_oov_buckets=1)
        ids = table.lookup(sparse_text)

        text_embedding_w = tf.Variable(
            tf.random_uniform([len(self.vocab) + 1, self.embedding_dim], -0.1, 0.1),
            name="embedding")

        text_embedding = tf.nn.embedding_lookup_sparse(text_embedding_w, ids, sp_weights=None, combiner="mean")

        logits = tf.layers.dense(
            inputs=text_embedding, units=self.num_classes,
            activation=None)

        self.logits = logits

        regularization_penalty = tf.contrib.layers.apply_regularization(
            tf.contrib.layers.l2_regularizer(scale=self.regularize_coef),
            tf.trainable_variables(scope="dense/"))

        predictions = tf.cast(tf.argmax(logits, axis=-1), tf.int32)
        self.probs = tf.nn.softmax(logits)

        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=self.Y, logits=logits))
        loss = loss + regularization_penalty
        tf.summary.scalar("loss", loss)

        opt = tf.train.AdamOptimizer(self.learning_rate)

        self.train_op = opt.minimize(loss, global_step=tf.train.get_global_step())

        self.accuracy = tf.reduce_mean(tf.cast(tf.equal(self.Y, predictions), tf.float32))
        tf.summary.scalar("accuracy", self.accuracy)

        self.merged_summary = tf.summary.merge_all()

