import numpy as np
import tensorflow as tf

class CNN():
    def __init__(self, embeddings, num_classes, learning_rate=0.001):
        self.embeddings = embeddings
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.create_inputs()
        self.create_graph()

    def create_inputs(self):
        self.X = tf.placeholder(dtype=tf.string, name="X", shape=[None])
        self.Y = tf.placeholder(dtype=tf.int64, name="Y", shape=[None])
        self.keep_prob = tf.placeholder_with_default(1., shape=[], name="keep_prob")

    def create_graph(self):
        sparse_text = tf.string_split(self.X, " ")
        lookup_table = tf.contrib.lookup.index_table_from_tensor(
                mapping=tf.constant(list(self.embeddings.vocab.keys())),
                num_oov_buckets=1)

        ids_sparse = lookup_table.lookup(sparse_text)
        ids = tf.sparse_tensor_to_dense(ids_sparse, default_value=len(self.embeddings.vocab))

        embed_dim = self.embeddings.vector_size

        embedding = tf.Variable(
                np.vstack((self.embeddings.vectors, np.zeros(embed_dim))),
                trainable=False,
                dtype=tf.float32)
        embedded = tf.nn.embedding_lookup(embedding, ids)

        embedded = tf.expand_dims(embedded, 3)

        conv2 = tf.layers.conv2d(embedded, filters=2, kernel_size=(2, embed_dim), activation=tf.nn.relu)
        conv2_squeezed = tf.squeeze(conv2, axis=-2)
        max_pooled2 = tf.reduce_max(conv2_squeezed, axis=-2, name="max_pool2")

        conv3 = tf.layers.conv2d(embedded, filters=2, kernel_size=(3, embed_dim), activation=tf.nn.relu)
        conv3_squeezed = tf.squeeze(conv3, axis=-2)
        max_pooled3 = tf.reduce_max(conv3_squeezed, axis=-2, name="max_pool3")

        conv4 = tf.layers.conv2d(embedded, filters=2, kernel_size=(4, embed_dim), activation=tf.nn.relu)
        conv4_squeezed = tf.squeeze(conv4, axis=-2)
        max_pooled4 = tf.reduce_max(conv4_squeezed, axis=-2, name="max_pool4")

        max_pooled = tf.concat((max_pooled2, max_pooled3, max_pooled4), axis=1)
        dropped_out = tf.nn.dropout(max_pooled, keep_prob=self.keep_prob)

        logits = tf.layers.dense(dropped_out, units=self.num_classes, name="final_dense")
        predictions = tf.argmax(logits, axis=1, name="argmax")

        self.logits = logits

        losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=self.logits, labels=self.Y)
        loss = tf.reduce_mean(losses)
        tf.summary.scalar("loss", loss)

        opt = tf.train.AdamOptimizer(self.learning_rate)
        self.train_op = opt.minimize(loss, global_step=tf.train.get_global_step())

        self.accuracy = tf.reduce_mean(tf.cast(tf.equal(self.Y, predictions), tf.float32))
        tf.summary.scalar("accuracy", self.accuracy)

        self.merged_summary = tf.summary.merge_all()
        
