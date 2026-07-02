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

const collectPage = readFileSync(join(process.cwd(), 'src', 'components', 'student', 'honors', 'achievement-collect.vue'), 'utf8')
assert.ok(collectPage.includes('教学成果类'), '成果收集页应提供教学成果类入口')
assert.ok(collectPage.includes('科研成果类'), '成果收集页应提供科研成果类入口')
assert.ok(collectPage.includes('recognizeTeachingReward'), '教学成果类应调用后端奖励规则识别接口')
assert.ok(collectPage.includes('label="奖项内容"'), '科研成果类应包含奖项内容输入框')
assert.ok(collectPage.includes('label="奖金数额"'), '科研成果类应包含奖金数额输入框')
assert.ok(!collectPage.includes('teaching-reward-apply'), '成果收集页不应引用旧教学奖励申报路由')

console.log('teaching reward policy helpers ok')
