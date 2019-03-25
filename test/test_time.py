import unittest
import logging
from test_context import cairo_utils as utils
import cairo_utils.time as time
from cairo_utils.time.arc import Arc
from cairo_utils.time.event import Event
import IPython
t = time.Time

class TestTime(unittest.TestCase):

    def setUp(self):
        return 1

    def tearDown(self):
        return 1

    #----------
    # ARC TESTS
    def test_arc_creation(self):
        an_arc = Arc(t(0,1), t(1,1))
        self.assertIsNotNone(an_arc)

    def test_arc_contains_true(self):
        an_arc = Arc(t(0,1), t(1,1))
        self.assertTrue(t(1,4) in an_arc)
        self.assertTrue(t(3,4) in an_arc)

    def test_arc_contains_false(self):
        an_arc = Arc(t(0,1), t(1,2))
        self.assertFalse(t(3,4) in an_arc)

    #get the size from the arc
    def test_arc_size(self):
        an_arc = Arc(t(1,4), t(1,2))
        self.assertEqual(an_arc.size(), t(1,4))

    #--------------------
    # EVENT TESTS
    def test_event_creation(self):
        anEvent = Event(Arc(t(0,1), t(1,1)), "a")
        self.assertIsNotNone(anEvent)

    #call an event
    def test_event_call(self):
        anEvent = Event(Arc(t(0,1), t(1,1)), "a")
        callResult = anEvent(t(1,2))
        self.assertEqual(len(callResult), 1)

    def test_event_call_outside_range(self):
        anEvent = Event(Arc(t(0,1), t(1,1)), "a")
        callResult = anEvent(t(2,1))
        self.assertEqual(len(callResult), 0)

    #call an event that holds a pattern
    def test_event_call_pattern(self):
        aPattern = time.Pattern(Arc(t(0,1),t(1,1)),
                           [ Event(Arc(t(0,1),t(1,2)), "a"),
                             Event(Arc(t(1,2),t(1,1)), "b"),
                           ])
        anEvent = Event(Arc(t(0,1), t(1,1)), aPattern, True)
        callResult = anEvent(t(1,2))
        self.assertEqual(len(callResult), 1)
        self.assertEqual(callResult[0].value, "b")

    #get the base set
    def test_event_base(self):
        anEvent = Event(Arc(t(0,1),t(1,1)), "a")
        base = anEvent.base()
        self.assertEqual(len(base), 2)

    def test_event_base_pattern(self):
        aPattern = time.Pattern(Arc(t(0,1),t(1,1)),
                                [ Event(Arc(t(1,4),t(1,2)), "a"),
                                  Event(Arc(t(1,6),t(3,8)), "b") ])
        anEvent = Event(Arc(t(0,1),t(1,1)), aPattern, True)
        base = anEvent.base()
        self.assertEqual(len(base), 6)

    #get the key
    def test_event_get_key(self):
        anEvent = Event(Arc(t(0,1),t(1,1)), "a")
        key = anEvent.key()
        self.assertEqual(key, t(0,1))

    #sort by key
    def test_event_sort_by_key(self):
        events = [ Event(Arc(t(1,2),t(1,1)), "a"),
                   Event(Arc(t(0,1),t(1,2)), "b"),
                   Event(Arc(t(2,1),t(3,1)), "c")]
        sorted_events = sorted(events, key=lambda x: x.key())
        values = [x.value for x in sorted_events]
        self.assertEqual(values, ["b","a","c"])

    #check contains
    def test_event_contains(self):
        anEvent = Event(Arc(t(0,1),t(1,2)), "a")
        self.assertTrue(t(1,4) in anEvent)
        self.assertFalse(t(3,4) in anEvent)

    #--------------------
    # PATTERN TESTS
    def test_pattern_creation(self):
        aPattern = time.Pattern(Arc(t(0,1), t(1,1)), [])
        self.assertIsNotNone(aPattern)

    #call empty
    def test_pattern_call_empty(self):
        aPattern = time.Pattern(Arc(t(0,1),t(1,1)), [])
        self.assertEqual(len(aPattern(t(0,1))), 0)

    #call with events
    def test_pattern_call(self):
        aPattern = time.Pattern(Arc(t(0,1), t(1,1)),
                                [ Event(Arc(t(0,1),t(1,2)), "a"),
                                  Event(Arc(t(1,2),t(1,1)), "b")])
        res = aPattern(t(1,2))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].value, "b")

    #call with patterns
    def test_pattern_call_with_internal_pattern_start(self):
        aPattern = time.Pattern(Arc(t(0,1), t(1,2)),
                                [ Event(Arc(t(0,1), t(1,2)), "a"),
                                  Event(Arc(t(1,2),t(1,1)), "b") ])

        mainPattern = time.Pattern(Arc(t(0,1), t(1,1)),
                                   [ Event(Arc(t(0,1), t(1,1)), "c"),
                                     aPattern ])

        result = mainPattern(t(0,1), True)
        self.assertEqual(len(result), 2)
        self.assertTrue("a" in result)
        self.assertTrue("c" in result)
        self.assertFalse("b" in result)

    def test_pattern_call_with_internal_pattern_scale(self):
        aPattern = time.Pattern(Arc(t(0,1), t(1,2)),
                                [ Event(Arc(t(0,1), t(1,2)), "a"),
                                  Event(Arc(t(1,2),t(1,1)), "b") ])

        mainPattern = time.Pattern(Arc(t(0,1), t(1,1)),
                                   [ Event(Arc(t(0,1), t(1,1)), "c"),
                                     aPattern ])

        #checks the internal pattern is scaled appropriately:
        result = mainPattern(t(1,4), True)
        self.assertEqual(len(result), 2)
        self.assertFalse("a" in result)
        self.assertTrue("b" in result)
        self.assertTrue("c" in result)

    def test_pattern_call_with_internal_pattern_end(self):
        aPattern = time.Pattern(Arc(t(0,1), t(1,2)),
                                [ Event(Arc(t(0,1), t(1,2)), "a"),
                                  Event(Arc(t(1,2),t(1,1)), "b") ])

        mainPattern = time.Pattern(Arc(t(0,1), t(1,1)),
                                   [ Event(Arc(t(0,1), t(1,1)), "c"),
                                     aPattern ])

        #checks the internal pattern ends appropriately:
        result = mainPattern(t(1,2), True)
        self.assertEqual(len(result), 1)
        self.assertTrue("c" in result)
        self.assertFalse("a" in result)
        self.assertFalse("b" in result)

    #call with patterns in events
    def test_pattern_call_with_patterns_in_events(self):
        aPattern = time.Pattern(Arc(t(0,1), t(1,2)),
                                [ Event(Arc(t(0,1), t(1,2)), "a"),
                                  Event(Arc(t(1,2),t(1,1)),  "b") ])

        mainPattern = time.Pattern(Arc(t(0,1), t(1,1)),
                                   [ Event(Arc(t(0,1), t(1,1)), "c"),
                                     Event(Arc(t(1,4), t(3,4)),
                                           aPattern, True) ])

        #checks the internal pattern ends appropriately:
        result = mainPattern(t(0,2), True)
        self.assertTrue("c" in result)
        self.assertFalse("a" in result)
        result2 = mainPattern(t(1,4), True)
        self.assertTrue("c" in result2)
        self.assertTrue("a" in result2)
        result3 = mainPattern(t(1,2), True)
        self.assertTrue("c" in result3)
        self.assertFalse("a" in result3)
        self.assertTrue("b" in result3)
        result4 = mainPattern(t(3,4), True)
        self.assertTrue("c" in result4)
        self.assertFalse("a" in result4)
        self.assertFalse("b" in result4)

    #get the key
    def test_pattern_get_key(self):
        aPattern = time.Pattern(Arc(t(3,8),t(6,8)),
                                [ Event(Arc(t(0,1),t(1,1)), "a")])

        self.assertEqual(aPattern.key(), t(3,8))

    #check contains
    def test_pattern_contains(self):
        aPattern = time.Pattern(Arc(t(3,8),t(6,8)),
                                [ Event(Arc(t(0,1),t(1,1)), "a")])

        self.assertTrue(t(4,8) in aPattern)
        self.assertFalse(t(7,8) in aPattern)

    #get the base set

    #pretty print pattern

    #--------------------
    # PARSER TESTS

    #Parse a pattern
    def test_parse_simple(self):
        aPattern = time.parse_string("[ a b c ]")
        IPython.embed(simple_prompt=True)
    #Parse a nested pattern

    #parse a pretty printed pattern

if __name__ == "__main__":
      #use python $filename to use this logging setup
      LOGLEVEL = logging.INFO
      logFileName = "log.test_time"
      logging.basicConfig(filename=logFileName, level=LOGLEVEL, filemode='w')
      console = logging.StreamHandler()
      console.setLevel(logging.INFO)
      logging.getLogger().addHandler(console)
      unittest.main()
      #reminder: user logging.getLogger().setLevel(logging.NOTSET) for log control