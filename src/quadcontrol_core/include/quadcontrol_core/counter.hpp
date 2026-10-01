#pragma once

class Counter {
public:
  void set_reset_requested(bool reset_requested)
  {
    reset_requested_ = reset_requested;
  }

  auto next_value() -> int
  {
    if (reset_requested_) {
      counter_ = 0;
      reset_requested_ = false;
    }

    return counter_++;
  }

private:
  bool reset_requested_{false};
  int counter_{0};
};
