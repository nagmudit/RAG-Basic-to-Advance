import math
import unittest
from training_bridge import example, finite_difference, loss_and_gradient, softmax


class TrainingBridgeTests(unittest.TestCase):
    def test_gradient_matches_independent_central_difference(self):
        for matrix in ([[1., 0.], [0., 1.]], [[.4, -.2], [.1, .8]]):
            for normalized in (False, True):
                kwargs = {"normalize": normalized, "temperature": .7}
                analytic = loss_and_gradient(matrix, **kwargs)["gradient"]
                numeric = finite_difference(matrix, **kwargs)
                for row, check in zip(analytic, numeric):
                    for a, n in zip(row, check):
                        self.assertAlmostEqual(a, n, places=7)

    def test_update_improves_positive_margin_and_loss(self):
        record = example()
        before, after = record["before"], record["after"]
        self.assertLess(after["loss"], before["loss"])
        self.assertGreater(after["scores"][0], before["scores"][0])
        self.assertLess(after["scores"][1], before["scores"][1])
        self.assertLess(record["finite_difference_max_error"], 1e-8)

    def test_constant_shift_preserves_probability_and_avoids_overflow(self):
        direct = [math.exp(x) for x in (4., 3., 1.)]
        expected = [x/sum(direct) for x in direct]
        for logits in ([4., 3., 1.], [0., -1., -3.], [1004., 1003., 1001.]):
            for got, want in zip(softmax(logits), expected):
                self.assertAlmostEqual(got, want, places=14)
        with self.assertRaises(OverflowError):
            math.exp(1004.)


if __name__ == "__main__":
    unittest.main()
