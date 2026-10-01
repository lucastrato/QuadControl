#include <gtest/gtest.h>

#include <quadcontrol_core/counter.hpp>

TEST(CounterTest, StartsAtZeroAndIncrements) {
  Counter counter;

  EXPECT_EQ(counter.next_value(), 0);
  EXPECT_EQ(counter.next_value(), 1);
  EXPECT_EQ(counter.next_value(), 2);
}

TEST(CounterTest, ResetMakesNextValueZero) {
  Counter counter;
  EXPECT_EQ(counter.next_value(), 0);
  EXPECT_EQ(counter.next_value(), 1);

  counter.set_reset_requested(true);

  EXPECT_EQ(counter.next_value(), 0);
  EXPECT_EQ(counter.next_value(), 1);
}

TEST(CounterTest, FalseResetRequestDoesNotResetCounter) {
  Counter counter;
  EXPECT_EQ(counter.next_value(), 0);
  counter.set_reset_requested(false);

  EXPECT_EQ(counter.next_value(), 1);
}
