import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import ts from 'typescript'

const sourcePath = join(process.cwd(), 'src', 'utils', 'teaching-reward-policy.ts')
const source = readFileSync(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2022,
  },
})

const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString('base64')}`
const policy = await import(moduleUrl)

const achievementRule = policy.rewardRules2024.find(
  rule => rule.category === 'teaching_achievement' && rule.level === 'national' && rule.rank === 'grand_prize',
)
assert.ok(achievementRule, '国家级教学成果特等奖规则应存在')
assert.equal(policy.rewardRuleKey(achievementRule), 'teaching_achievement--national--grand_prize')
assert.equal(policy.rewardContentLabel(achievementRule), '国家级教学成果特等奖')

const competitionRule = policy.rewardRules2024.find(
  rule => rule.category === 'teaching_competition' && rule.subcategory === 'group' && rule.level === 'provincial' && rule.rank === 'first_prize',
)
assert.ok(competitionRule, '省级教学竞赛团体一等奖规则应存在')
assert.equal(policy.rewardContentLabel(competitionRule), '省（部）级教学竞赛团体奖励一等奖')

const applyPage = readFileSync(join(process.cwd(), 'src', 'components', 'student', 'hr', 'TeachingRewardApply.vue'), 'utf8')
assert.match(applyPage, /Object\.entries\(categoryMap\)\.map\(\(\[value, label\]\) => \(\{\s*label,\s*value,\s*\}\)\)/s, '奖励类别下拉应直接使用 PDF 类别名称作为标签')
assert.ok(!applyPage.includes('教学专项奖 /'), '奖励类别下拉不应给 PDF 类别添加“教学专项奖 /”前缀')

console.log('teaching reward policy helpers ok')
