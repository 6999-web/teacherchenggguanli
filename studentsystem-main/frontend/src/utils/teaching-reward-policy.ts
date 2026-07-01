export type RewardRuleOption = {
  category: string
  subcategory?: string
  level?: string
  rank?: string
  amount: number
  staged?: boolean
  annual_cap?: number
  manual_required?: boolean
  allow_duplicate?: boolean
}

export const categoryMap: Record<string, string> = {
  teaching_achievement: '教学成果类',
  major_construction: '专业建设类',
  course_construction: '课程建设类',
  textbook_construction: '教材建设类',
  practice_teaching: '实践教学建设类',
  teaching_competition: '教学竞赛类',
  teacher_team: '教师队伍建设类',
  teaching_reform: '教学改革项目奖',
  teaching_quality: '教学质量奖',
  lecture_competition: '讲课比赛奖',
  sanquan_education: '三全育人专项奖',
  teaching_management: '教学管理奖',
  ideological_political: '思政类教学工作专项奖',
}

export const levelMap: Record<string, string> = {
  national: '国家级',
  provincial: '省（部）级',
  municipal: '市（厅）级',
  school: '校级',
}

export const rankMap: Record<string, string> = {
  grand_prize: '特等奖',
  first_prize: '一等奖',
  second_prize: '二等奖',
  third_prize: '三等奖',
  key: '重点项目',
  major: '重大项目',
  general: '一般项目',
  A: 'A类',
  B: 'B类',
}

export const rewardRules2024: RewardRuleOption[] = [
  { category: 'teaching_achievement', level: 'national', rank: 'grand_prize', amount: 120000 },
  { category: 'teaching_achievement', level: 'national', rank: 'first_prize', amount: 100000 },
  { category: 'teaching_achievement', level: 'national', rank: 'second_prize', amount: 80000 },
  { category: 'teaching_achievement', level: 'provincial', rank: 'grand_prize', amount: 60000 },
  { category: 'teaching_achievement', level: 'provincial', rank: 'first_prize', amount: 50000 },
  { category: 'teaching_achievement', level: 'provincial', rank: 'second_prize', amount: 30000 },
  { category: 'teaching_achievement', level: 'municipal', rank: 'grand_prize', amount: 8000 },
  { category: 'teaching_achievement', level: 'municipal', rank: 'first_prize', amount: 6000 },
  { category: 'teaching_achievement', level: 'municipal', rank: 'second_prize', amount: 4000 },
  { category: 'teaching_achievement', level: 'school', rank: 'grand_prize', amount: 3000 },
  { category: 'teaching_achievement', level: 'school', rank: 'first_prize', amount: 2000 },
  { category: 'teaching_achievement', level: 'school', rank: 'second_prize', amount: 1000 },

  { category: 'major_construction', subcategory: '特色专业/一流专业/现代产业学院', level: 'national', amount: 60000 },
  { category: 'major_construction', subcategory: '特色专业/一流专业/现代产业学院', level: 'provincial', amount: 40000 },
  { category: 'major_construction', subcategory: '特色专业/一流专业/现代产业学院', level: 'school', amount: 10000 },
  { category: 'course_construction', subcategory: '精品/一流/示范课程', level: 'national', amount: 50000 },
  { category: 'course_construction', subcategory: '精品/一流/示范课程', level: 'provincial', amount: 30000 },

  { category: 'textbook_construction', subcategory: '教材出版20万字以上', level: 'school', amount: 8000 },
  { category: 'textbook_construction', subcategory: '教材出版20万字以下', level: 'school', amount: 6000 },
  { category: 'textbook_construction', subcategory: '优秀教材奖', level: 'national', rank: 'first_prize', amount: 50000 },
  { category: 'textbook_construction', subcategory: '优秀教材奖', level: 'national', rank: 'second_prize', amount: 30000 },
  { category: 'textbook_construction', subcategory: '优秀教材奖', level: 'national', rank: 'third_prize', amount: 20000 },
  { category: 'textbook_construction', subcategory: '优秀教材奖', level: 'provincial', rank: 'first_prize', amount: 15000 },
  { category: 'textbook_construction', subcategory: '优秀教材奖', level: 'provincial', rank: 'second_prize', amount: 10000 },
  { category: 'textbook_construction', subcategory: '优秀教材奖', level: 'provincial', rank: 'third_prize', amount: 5000 },

  { category: 'practice_teaching', subcategory: '示范性实训基地/校外实践教学基地', level: 'national', amount: 80000 },
  { category: 'practice_teaching', subcategory: '重点实验室', level: 'national', amount: 80000 },
  { category: 'practice_teaching', subcategory: '重点实验室', level: 'provincial', amount: 30000 },
  { category: 'practice_teaching', subcategory: '示范性实训基地/校外实践教学基地', level: 'provincial', amount: 20000 },

  { category: 'teaching_competition', subcategory: 'group', level: 'national', rank: 'grand_prize', amount: 30000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'national', rank: 'first_prize', amount: 20000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'national', rank: 'second_prize', amount: 15000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'national', rank: 'third_prize', amount: 10000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'provincial', rank: 'grand_prize', amount: 10000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'provincial', rank: 'first_prize', amount: 8000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'provincial', rank: 'second_prize', amount: 6000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'provincial', rank: 'third_prize', amount: 5000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'municipal', rank: 'first_prize', amount: 5000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'municipal', rank: 'second_prize', amount: 3000 },
  { category: 'teaching_competition', subcategory: 'group', level: 'municipal', rank: 'third_prize', amount: 2000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'national', rank: 'grand_prize', amount: 20000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'national', rank: 'first_prize', amount: 15000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'national', rank: 'second_prize', amount: 12000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'national', rank: 'third_prize', amount: 8000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'provincial', rank: 'grand_prize', amount: 8000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'provincial', rank: 'first_prize', amount: 6000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'provincial', rank: 'second_prize', amount: 4000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'provincial', rank: 'third_prize', amount: 3000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'municipal', rank: 'first_prize', amount: 3000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'municipal', rank: 'second_prize', amount: 2000, annual_cap: 20000 },
  { category: 'teaching_competition', subcategory: 'individual', level: 'municipal', rank: 'third_prize', amount: 1000, annual_cap: 20000 },

  { category: 'teacher_team', subcategory: '优秀教学团队', level: 'national', amount: 60000 },
  { category: 'teacher_team', subcategory: '优秀教学团队', level: 'provincial', amount: 30000 },
  { category: 'teacher_team', subcategory: '优秀教学团队', level: 'school', amount: 10000 },
  { category: 'teacher_team', subcategory: '教学名师', level: 'national', amount: 50000 },
  { category: 'teacher_team', subcategory: '教学名师', level: 'provincial', amount: 30000 },
  { category: 'teacher_team', subcategory: '教学名师', level: 'school', amount: 5000 },
  { category: 'teacher_team', subcategory: '教学新秀', level: 'school', amount: 2000 },

  { category: 'teaching_reform', subcategory: '重点/重大项目', level: 'national', rank: 'key', amount: 30000, staged: true },
  { category: 'teaching_reform', subcategory: '重点/重大项目', level: 'national', rank: 'major', amount: 30000, staged: true },
  { category: 'teaching_reform', subcategory: '一般项目', level: 'national', rank: 'general', amount: 15000, staged: true },
  { category: 'teaching_reform', subcategory: '本科教改重点项目', level: 'provincial', rank: 'key', amount: 10000, staged: true },
  { category: 'teaching_reform', subcategory: '本科教改一般A类/职教重点', level: 'provincial', rank: 'A', amount: 6000, staged: true },
  { category: 'teaching_reform', subcategory: '本科教改一般B类/职教一般', level: 'provincial', rank: 'B', amount: 3000, staged: true },
  { category: 'teaching_quality', level: 'school', rank: 'first_prize', amount: 3000 },
  { category: 'teaching_quality', level: 'school', rank: 'second_prize', amount: 2000 },
  { category: 'teaching_quality', level: 'school', rank: 'third_prize', amount: 1000 },
  { category: 'lecture_competition', level: 'school', rank: 'first_prize', amount: 3000 },
  { category: 'lecture_competition', level: 'school', rank: 'second_prize', amount: 2000 },
  { category: 'lecture_competition', level: 'school', rank: 'third_prize', amount: 1000 },

  { category: 'sanquan_education', subcategory: '三全育人综合改革示范校', level: 'national', amount: 80000 },
  { category: 'sanquan_education', subcategory: '三全育人综合改革示范校', level: 'provincial', amount: 40000 },
  { category: 'sanquan_education', subcategory: '三全育人综合改革示范院系', level: 'national', amount: 40000 },
  { category: 'sanquan_education', subcategory: '三全育人综合改革示范院系', level: 'provincial', amount: 20000 },
  { category: 'teaching_management', subcategory: '虚拟教研室/示范中心', level: 'national', amount: 50000 },
  { category: 'teaching_management', subcategory: '虚拟教研室/示范中心', level: 'provincial', amount: 30000 },
  { category: 'teaching_management', subcategory: '基层教学组织', level: 'provincial', amount: 20000 },
  { category: 'teaching_management', subcategory: '教学管理工作先进单位', level: 'school', amount: 15000 },
  { category: 'teaching_management', subcategory: '教研室工作先进单位', level: 'school', amount: 5000 },
]

export function optionLabel(map: Record<string, string>, value?: string | null) {
  return value ? map[value] || value : '无'
}

export function ruleTitle(rule: RewardRuleOption) {
  return [
    optionLabel(categoryMap, rule.category),
    rule.subcategory && !['group', 'individual'].includes(rule.subcategory) ? rule.subcategory : '',
    optionLabel(levelMap, rule.level),
    optionLabel(rankMap, rule.rank),
    rule.subcategory === 'group' ? '团体奖励' : '',
    rule.subcategory === 'individual' ? '单项奖励' : '',
  ].filter(Boolean).join(' / ')
}

export function rewardRuleKey(rule: RewardRuleOption) {
  return [rule.category, rule.subcategory, rule.level, rule.rank].filter(Boolean).join('--')
}

export function rewardContentLabel(rule: RewardRuleOption) {
  const level = optionLabel(levelMap, rule.level)
  const rank = optionLabel(rankMap, rule.rank)
  const category = optionLabel(categoryMap, rule.category)
  const subcategory = rule.subcategory && !['group', 'individual'].includes(rule.subcategory) ? rule.subcategory : ''

  if (rule.category === 'teaching_achievement') {
    return `${level}教学成果${rank}`
  }

  if (rule.category === 'teaching_competition') {
    const scope = rule.subcategory === 'group' ? '团体奖励' : '单项奖励'
    return `${level}教学竞赛${scope}${rank}`
  }

  if (rule.category === 'teaching_quality' || rule.category === 'lecture_competition') {
    return `${category}${rank}`
  }

  if (rule.category === 'teaching_reform') {
    return `${level}${subcategory || '教学改革项目'}${rank}`
  }

  return [level, subcategory || category, rank].filter(part => part && part !== '无').join('')
}

export function money(value: number) {
  return `${Number(value || 0).toLocaleString('zh-CN')} 元`
}
