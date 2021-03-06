"""Unit tests for result.py"""

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from tournaments.models import Round, Tournament
from participants.models import Adjudicator, Institution, Speaker, Team
from venues.models import Venue
from draw.models import Debate, DebateTeam
from results.models import BallotSubmission
from adjallocation.models import DebateAdjudicator

from ..result import BallotSet


class BaseTestResult(TestCase):

    testdata = dict()
    testdata[1] = {
        'scores': [[[75.0, 76.0, 74.0, 38.0], [76.0, 73.0, 75.0, 37.5]],
                   [[74.0, 75.0, 76.0, 37.0], [77.0, 74.0, 74.0, 38.0]],
                   [[75.0, 75.0, 75.0, 37.5], [76.0, 78.0, 77.0, 37.0]]],
        'totals_by_adj': [[263, 261.5], [262, 263], [262.5, 268]],
        'majority_scores': [[74.5, 75, 75.5, 37.25], [76.5, 76, 75.5, 37.5]],
        'majority_totals': [262.25, 265.5],
        'winner_by_adj': [0, 1, 1],
        'winner': 1,
        'num_adjs_for_team': [1, 2]
    }
    testdata[2] = {
        'scores': [[[73.0, 76.0, 79.0, 37.5], [77.0, 77.0, 78.0, 39.0]],
                   [[79.0, 80.0, 70.0, 36.0], [78.0, 79.0, 73.0, 37.0]],
                   [[73.0, 70.0, 77.0, 35.0], [76.0, 76.0, 77.0, 37.0]]],
        'totals_by_adj': [[265.5, 271.0], [265.0, 267.0], [255.0, 266.0]],
        'majority_scores': [[75.0, 75.33333333333333, 75.33333333333333, 36.166666666666664],
                            [77.0, 77.33333333333333, 76.0, 37.666666666666664]],
        'majority_totals': [261.8333333333333, 268.0],
        'winner_by_adj': [1, 1, 1],
        'winner': 1,
        'num_adjs_for_team': [0, 3],
    }
    testdata[3] = {
        'majority_scores': [[75.5, 76.5, 77.5, 38.75], [71.5, 71.5, 75.0, 38.5]],
        'winner': 0,
        'winner_by_adj': [1, 0, 0],
        'totals_by_adj': [[261.0, 271.5], [268.5, 259.0], [268.0, 254.0]],
        'majority_totals': [268.25, 256.5],
        'scores': [[[73.0, 70.0, 78.0, 40.0], [80.0, 78.0, 75.0, 38.5]],
                   [[79.0, 75.0, 75.0, 39.5], [73.0, 73.0, 73.0, 40.0]],
                   [[72.0, 78.0, 80.0, 38.0], [70.0, 70.0, 77.0, 37.0]]],
        'num_adjs_for_team': [2, 1],
    }

    incompletedata = {'scores': [[[75, 76, None, 38],   [76, 73, 75, 37.5]],
                                 [[74, 75, 76, 37],   [77, None, 74, 38]],
                                 [[75, 75, 75, 37.5], [76, 78, 77, None]]],
                      'totals_by_adj': [[None, 261.5], [262, None], [262.5, None]],
                      'majority_scores': [[None, 75, 75.5, 37.25], [76.5, None, 75.5, None]],
                      'majority_totals': [None, None],
                      'winner_by_adj': [None, None, None],
                      'winner': None,
                      'num_adjs_for_team': [None, None]}

    def setUp(self):
        self.t = Tournament.objects.create(slug="resulttest", name="ResultTest")
        for i in range(2):
            inst = Institution.objects.create(code="Inst{:d}".format(i), name="Institution {:d}".format(i))
            team = Team.objects.create(tournament=self.t, institution=inst, reference="Team {:d}".format(i), use_institution_prefix=False)
            for j in range(3):
                Speaker.objects.create(team=team, name="Speaker %d-%d" % (i, j))
        inst = Institution.objects.create(code="Adjs", name="Adjudicators")
        for i in range(3):
            Adjudicator.objects.create(tournament=self.t, institution=inst, name="Adjudicator {:d}".format(i), test_score=5)
        venue = Venue.objects.create(name="Venue", priority=10)

        self.adjs = list(Adjudicator.objects.all())
        self.teams = list(Team.objects.all())

        rd = Round.objects.create(tournament=self.t, seq=1, abbreviation="R1")
        self.debate = Debate.objects.create(round=rd, venue=venue)

        positions = [DebateTeam.POSITION_AFFIRMATIVE, DebateTeam.POSITION_NEGATIVE]
        for team, pos in zip(self.teams, positions):
            DebateTeam.objects.create(debate=self.debate, team=team, position=pos)
        adjtypes = [DebateAdjudicator.TYPE_CHAIR, DebateAdjudicator.TYPE_PANEL, DebateAdjudicator.TYPE_PANEL]
        for adj, adjtype in zip(self.adjs, adjtypes):
            DebateAdjudicator.objects.create(debate=self.debate, adjudicator=adj, type=adjtype)

    def tearDown(self):
        self.t.delete()
        Institution.objects.all().delete()

    def _get_team(self, team):
        if team in ['aff', 'neg']:
            team = self.debate.get_team(team)
        return team

    def _get_ballotset(self):
        ballotsub = BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        return BallotSet(ballotsub)

    def save_complete_ballotset(self, teams, testdata):
        self._save_complete_ballotset(teams, testdata)

    def _save_complete_ballotset(self, teams, testdata, post_ballotset_create=None):
        # unconfirm existing ballot
        try:
            existing = BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        except BallotSubmission.DoesNotExist:
            pass
        else:
            existing.confirmed = False
            existing.save()

        ballotsub = BallotSubmission(debate=self.debate, submitter_type=BallotSubmission.SUBMITTER_TABROOM)
        ballotset = BallotSet(ballotsub)
        if post_ballotset_create:
            post_ballotset_create(ballotset)
        scores = testdata['scores']

        for team in teams:
            speakers = self._get_team(team).speaker_set.all()
            for pos, speaker in enumerate(speakers, start=1):
                ballotset.set_speaker(team, pos, speaker)
            ballotset.set_speaker(team, 4, speakers[0])

        for adj, sheet in zip(self.adjs, scores):
            for team, teamscores in zip(teams, sheet):
                for pos, score in enumerate(teamscores, start=1):
                    ballotset.set_score(adj, team, pos, score)

        ballotset.confirmed = True
        ballotset.save()

        return ballotset


class CommonTests(object):

    def on_all_datasets(test_fn):  # flake8: noqa
        """Decorator.
        Tests should be written to take three arguments: self, ballotset and
        testdata. 'ballotset' is a BallotSet object. 'testdata' is a value of
        BaseTestResult.testdata.
        This decorator then sets up the BallotSet and runs the test once for
        each test dataset in BaseTestResult.testdata."""
        def foo(self):
            for testdata_key in self.testdata:
                testdata = self.testdata[testdata_key]
                self.save_complete_ballotset(self.teams_input, testdata)
                ballotset = self._get_ballotset()
                test_fn(self, ballotset, testdata)
        return foo

    @on_all_datasets
    def test_save_complete_ballotset(self, ballotset, testdata):
        # Just run self.save_complete_ballotset
        pass

    @on_all_datasets
    def test_totals_by_adj(self, ballotset, testdata):
        for adj, totals in zip(self.adjs, testdata['totals_by_adj']):
            for team, total in zip(self.teams_input, totals):
                self.assertEqual(ballotset.adjudicator_sheets[adj].get_total(team), total)

    @on_all_datasets
    def test_totals_by_adj_by_side(self, ballotset, testdata):
        for adj, totals in zip(self.adjs, testdata['totals_by_adj']):
            self.assertEqual(ballotset.adjudicator_sheets[adj].aff_score, totals[0])
            self.assertEqual(ballotset.adjudicator_sheets[adj].neg_score, totals[1])

    @on_all_datasets
    def test_majority_scores(self, ballotset, testdata):
        for team, totals in zip(self.teams_input, testdata['majority_scores']):
            for pos, score in enumerate(totals, start=1):
                self.assertEqual(ballotset.get_avg_score(team, pos), score)

    @on_all_datasets
    def test_individual_scores(self, ballotset, testdata):
        for adj, sheet in zip(self.adjs, testdata['scores']):
            for team, totals in zip(self.teams_input, sheet):
                for pos, score in enumerate(totals, start=1):
                    self.assertEqual(ballotset.get_score(adj, team, pos), score)

    @on_all_datasets
    def test_winner_by_adj(self, ballotset, testdata):
        for adj, winner in zip(self.adjs, testdata['winner_by_adj']):
            self.assertEqual(ballotset.adjudicator_sheets[adj].winner,
                self.teams[winner])

    @on_all_datasets
    def test_winner_by_adj_by_side(self, ballotset, testdata):
        for adj, winner in zip(self.adjs, testdata['winner_by_adj']):
            self.assertEqual(ballotset.adjudicator_sheets[adj].aff_win,
                winner == 0)
            self.assertEqual(ballotset.adjudicator_sheets[adj].neg_win,
                winner == 1)

    @on_all_datasets
    def test_num_adjs_for_team(self, ballotset, testdata):
        for team, num_adjs in zip(self.teams_input, testdata['num_adjs_for_team']):
            self.assertEqual(ballotset.num_adjs_for_team(team), num_adjs)

    @on_all_datasets
    def test_winner(self, ballotset, testdata):
        self.assertEqual(ballotset.winner, self.teams[testdata['winner']])

    @on_all_datasets
    def test_winner_by_side(self, ballotset, testdata):
        self.assertEqual(ballotset.aff_win, testdata['winner'] == 0)
        self.assertEqual(ballotset.neg_win, testdata['winner'] == 1)

    @on_all_datasets
    def test_majority_totals(self, ballotset, testdata):
        for team, total in zip(self.teams_input, testdata['majority_totals']):
            self.assertAlmostEqual(ballotset.get_avg_total(team), total)

    @on_all_datasets
    def test_majority_totals_by_side(self, ballotset, testdata):
        self.assertAlmostEqual(ballotset.aff_score, testdata['majority_totals'][0])
        self.assertAlmostEqual(ballotset.neg_score, testdata['majority_totals'][1])

    @on_all_datasets
    def test_sheet_iter(self, ballotset, testdata):
        names = ["1", "2", "3", "Reply"]
        for sheet, adj, scores, total, winner in zip(ballotset.sheet_iter, self.adjs, testdata['scores'], testdata['totals_by_adj'], testdata['winner_by_adj']):
            self.assertEqual(sheet.adjudicator, adj)
            for pos, name, speaker, score in zip(sheet.affs, names, self._get_team('aff').speaker_set.all(), scores[0]):
                self.assertEqual(pos.name, name)
                self.assertEqual(pos.speaker, speaker)
                self.assertEqual(pos.score, score)
            for pos, name, speaker, score in zip(sheet.negs, names, self._get_team('neg').speaker_set.all(), scores[1]):
                self.assertEqual(pos.name, name)
                self.assertEqual(pos.speaker, speaker)
                self.assertEqual(pos.score, score)
            self.assertEqual(sheet.aff_score, total[0])
            self.assertEqual(sheet.neg_score, total[1])
            self.assertEqual(sheet.aff_win, winner == 0)
            self.assertEqual(sheet.neg_win, winner == 1)

    def test_incomplete_save(self):
        self.assertRaises(AssertionError, self.save_complete_ballotset, self.teams_input, self.incompletedata)


class TestResultByTeam(BaseTestResult, CommonTests):
    def setUp(self):
        super().setUp()
        self.teams_input = self.teams


class TestResultBySide(BaseTestResult, CommonTests):
    def setUp(self):
        super().setUp()
        self.teams_input = ['aff', 'neg']


class TestResultWithInitiallyUnknownSides(BaseTestResult, CommonTests):

    def setUp(self):
        super().setUp()
        for dt in self.debate.debateteam_set.all():
            dt.position = DebateTeam.POSITION_UNALLOCATED
            dt.save()
        self.teams_input = ['aff', 'neg']

    def save_complete_ballotset(self, teams, testdata):
        self._save_complete_ballotset(teams, testdata,
                post_ballotset_create=lambda ballotset: ballotset.set_sides(*self.teams))

    def test_unknown_sides(self):
        self.assertRaises(ObjectDoesNotExist, self._save_complete_ballotset,
                self.teams_input, list(self.testdata.values())[0])


class TestResultBadLoad(BaseTestResult, TestCase):

    def setUp(self):
        super().setUp()
        self.save_complete_ballotset(['aff', 'neg'], list(self.testdata.values())[0])

    def test_extraneous_speaker(self):
        ballotset = self._get_ballotset()
        ballotset.speakers["test"] = {}
        self.assertRaises(AssertionError, ballotset.assert_loaded)

    def test_extraneous_motion_veto(self):
        ballotset = self._get_ballotset()
        ballotset.motion_veto["test"] = None
        self.assertRaises(AssertionError, ballotset.assert_loaded)

    def test_extraneous_teamscore(self):
        ballotset = self._get_ballotset()
        ballotset.teamscore_objects["test"] = None
        self.assertRaises(AssertionError, ballotset.assert_loaded)

    def test_extraneous_speaker_position(self):
        ballotset = self._get_ballotset()
        list(ballotset.speakers.values())[0][6] = None
        self.assertRaises(AssertionError, ballotset.assert_loaded)

    def test_extraneous_sheet_score(self):
        ballotset = self._get_ballotset()
        sheet = list(ballotset.adjudicator_sheets.values())[0]
        list(sheet.data.values())[0][8] = None
        self.assertRaises(AssertionError, ballotset.assert_loaded)

    def test_missing_teamscore(self):
        ballotset = self._get_ballotset()
        ballotset.teamscore_objects.popitem()
        self.assertRaises(AssertionError, ballotset.assert_loaded)

    def test_missing_speaker(self):
        ballotset = self._get_ballotset()
        ballotset.speakers.popitem()
        self.assertRaises(AssertionError, ballotset.assert_loaded)
