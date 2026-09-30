/**
 * AWS Exam Scaled Score Calculator
 * Converts raw scores to AWS-style 0-1000 scaled scores
 */

class ExamScoring {
  constructor() {
    // AWS AI Practitioner exam parameters
    this.MIN_SCORE = 0;
    this.MAX_SCORE = 1000;
    this.PASSING_SCORE = 700; // Typical AWS exam passing score
    this.TOTAL_EXAM_QUESTIONS = 65; // Official AIF-C01 exam
  }

  /**
   * Calculate AWS-style scaled score
   * @param {number} correctAnswers - Number of correct answers
   * @param {number} totalQuestions - Total questions in test
   * @returns {object} Detailed scoring breakdown
   */
  calculateScaledScore(correctAnswers, totalQuestions) {
    // Calculate raw percentage
    const rawPercentage = (correctAnswers / totalQuestions) * 100;

    // AWS scaling formula (simplified but realistic)
    // Maps percentage to 0-1000 scale with realistic distribution
    const scaledScore = Math.round((rawPercentage / 100) * this.MAX_SCORE);

    // Calculate against official exam difficulty
    const examEquivalent = this.getExamEquivalent(scaledScore);

    // Determine performance level
    const performanceLevel = this.getPerformanceLevel(scaledScore);

    // Estimate readiness
    const readiness = this.getReadinessLevel(scaledScore);

    return {
      scaledScore: scaledScore,
      rawPercentage: Math.round(rawPercentage * 10) / 10, // 1 decimal place
      correctAnswers: correctAnswers,
      totalQuestions: totalQuestions,
      passingScore: this.PASSING_SCORE,
      passed: scaledScore >= this.PASSING_SCORE,
      performanceLevel: performanceLevel,
      readiness: readiness,
      examEquivalent: examEquivalent,
      scoreBreakdown: this.getScoreBreakdown(scaledScore),
      recommendation: this.getRecommendation(scaledScore)
    };
  }

  /**
   * Get what the scaled score means in exam context
   */
  getExamEquivalent(scaledScore) {
    if (scaledScore >= 900) return 'Expert Level';
    if (scaledScore >= 800) return 'Advanced Level';
    if (scaledScore >= 700) return 'Proficient Level (Passing)';
    if (scaledScore >= 600) return 'Intermediate Level';
    if (scaledScore >= 500) return 'Basic Level';
    return 'Foundational Level';
  }

  /**
   * Performance rating
   */
  getPerformanceLevel(scaledScore) {
    if (scaledScore >= 950) return 'Outstanding';
    if (scaledScore >= 900) return 'Excellent';
    if (scaledScore >= 800) return 'Very Good';
    if (scaledScore >= 700) return 'Good (Passing)';
    if (scaledScore >= 600) return 'Fair';
    if (scaledScore >= 500) return 'Needs Improvement';
    return 'Study Required';
  }

  /**
   * Exam readiness assessment
   */
  getReadinessLevel(scaledScore) {
    if (scaledScore >= 800) return 'Ready for Exam';
    if (scaledScore >= 700) return 'Likely to Pass';
    if (scaledScore >= 600) return 'Review Key Topics';
    if (scaledScore >= 500) return 'Continue Studying';
    return 'Significant Study Needed';
  }

  /**
   * Detailed score breakdown
   */
  getScoreBreakdown(scaledScore) {
    const ranges = [
      { min: 900, max: 1000, label: 'Expert', color: '#059669' },
      { min: 800, max: 899, label: 'Advanced', color: '#0891b2' },
      { min: 700, max: 799, label: 'Proficient', color: '#7c3aed' },
      { min: 600, max: 699, label: 'Intermediate', color: '#f59e0b' },
      { min: 500, max: 599, label: 'Basic', color: '#ef4444' },
      { min: 0, max: 499, label: 'Foundational', color: '#dc2626' }
    ];

    const current = ranges.find(r => scaledScore >= r.min && scaledScore <= r.max);
    return {
      current: current,
      ranges: ranges
    };
  }

  /**
   * Get personalized recommendation
   */
  getRecommendation(scaledScore) {
    if (scaledScore >= 850) {
      return 'Excellent preparation! You are well-prepared for the exam. Consider scheduling your test.';
    }
    if (scaledScore >= 750) {
      return 'Good progress! Review any flagged questions and focus on weaker domains before exam day.';
    }
    if (scaledScore >= 700) {
      return 'You\'re at the passing threshold. Review all domains thoroughly, especially weak areas.';
    }
    if (scaledScore >= 600) {
      return 'Continue studying. Focus on foundational concepts and practice more scenarios.';
    }
    if (scaledScore >= 500) {
      return 'Significant practice needed. Review core concepts and take more practice tests.';
    }
    return 'Build foundational knowledge first. Focus on learning core AWS AI services and concepts.';
  }

  /**
   * Calculate domain-specific scores
   */
  calculateDomainScores(domainResults) {
    const scores = {};
    for (const [domain, result] of Object.entries(domainResults)) {
      scores[domain] = this.calculateScaledScore(result.correct, result.total);
    }
    return scores;
  }

  /**
   * Get score percentile (mock - in real system would use historical data)
   */
  getPercentile(scaledScore) {
    // Simulated percentile based on normal distribution
    if (scaledScore >= 900) return 95;
    if (scaledScore >= 850) return 90;
    if (scaledScore >= 800) return 80;
    if (scaledScore >= 750) return 70;
    if (scaledScore >= 700) return 60;
    if (scaledScore >= 650) return 50;
    if (scaledScore >= 600) return 40;
    if (scaledScore >= 550) return 30;
    if (scaledScore >= 500) return 20;
    return 10;
  }
}

// Export for use in app
window.ExamScoring = ExamScoring;
