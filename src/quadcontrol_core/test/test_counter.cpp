#include <gtest/gtest.h>

#include <quadcontrol_core/counter.hpp>

/**
 * @brief Verifies the initial value and increment behavior of Counter.
 *
 * A newly constructed Counter starts at zero and returns consecutive
 * values on subsequent calls to next_value().
 */
TEST(CounterTest, StartsAtZeroAndIncrements) {
  Counter counter;

  EXPECT_EQ(counter.next_value(), 0);
  EXPECT_EQ(counter.next_value(), 1);
  EXPECT_EQ(counter.next_value(), 2);
}

/**
 * @brief Verifies that a requested reset makes the next value zero.
 *
 * After a reset request, the next call to next_value() returns zero
 * and subsequent calls resume normal incrementing.
 */
TEST(CounterTest, ResetMakesNextValueZero) {
  Counter counter;
  EXPECT_EQ(counter.next_value(), 0);
  EXPECT_EQ(counter.next_value(), 1);

  counter.set_reset_requested(true);

  EXPECT_EQ(counter.next_value(), 0);
  EXPECT_EQ(counter.next_value(), 1);
}

/**
 * @brief Verifies that a false reset request does not reset the counter.
 *
 * A reset request with a value of false must leave the current counter
 * sequence unchanged.
 */
TEST(CounterTest, FalseResetRequestDoesNotResetCounter) {
  Counter counter;
  EXPECT_EQ(counter.next_value(), 0);
  counter.set_reset_requested(false);

  EXPECT_EQ(counter.next_value(), 1);
}