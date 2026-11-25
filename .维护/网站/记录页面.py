import 新版页面 as site
VERSION='20261106-records-v3'

def page():
    body='''<link rel="stylesheet" href="assets/records.css?v=VERSION">
<div class="records-page"><div class="narrow">
<header class="records-heading"><h1>记录</h1><p>水质、加药与换水，按缸保存。 <a href="#records-entry-section">记一笔 ›</a></p><button id="records-auth" type="button">写入登录</button></header>
<p id="records-insecure" class="records-warning" hidden>当前入口仅供查看。请到<a href="https://dystudio.fun/fish/records.html">加密网址</a>录入和输入密码。</p>
<nav class="records-tabs" aria-label="选择缸"><button data-tank="qt" aria-selected="true" type="button">检疫桶</button><button data-tank="main" aria-selected="false" type="button">主缸</button></nav>
<div id="records-status" role="status" aria-live="polite">正在读取服务器记录…</div>
<section class="records-settings" aria-label="当前阶段和实际水量"><div><label for="records-phase">当前阶段</label><select id="records-phase"><option value="cycling">养水期（没有鱼）</option><option value="animals">检疫中（有鱼）</option></select></div><div><label for="records-volume">实际水量 · L</label><input id="records-volume" type="number" min="0.01" max="10000" step="0.01" inputmode="decimal" placeholder="加满后填写"></div><button id="records-settings-save" type="button">保存设置</button><span id="records-settings-status" role="status"></span></section>
<section class="records-next" aria-labelledby="records-next-heading"><div class="records-section-heading"><h2 id="records-next-heading">下一步做什么</h2><span id="records-rounds"></span></div><ul id="records-advice"><li>读取记录后按当前阶段计算。</li></ul><p class="records-note">提示照网站养护规则自动计算，最后以<a href="guide-qt.html">检疫桶养水 ›</a>为准。有动物时同时参考<a href="guide-quar.html">检疫观察 ›</a>。</p></section>

<section class="records-entry" id="records-entry-section"><div class="records-section-heading"><h2 id="records-form-title">记一笔</h2><span>测了哪项就填哪项</span></div><form id="records-form">
<div class="records-datetime"><label for="records-date">日期与时间 <small>上海时间</small></label><input id="records-date" name="observed_at" type="datetime-local" required></div>
<div class="records-form-columns"><fieldset class="records-measurements"><legend>水质</legend>
<div class="records-field records-nh3"><div class="records-field-label"><label for="records-reagent">NH3</label><span>mg/L</span></div><div class="records-control"><select id="records-reagent" name="nh3_reagent"><option value="yier">益尔</option><option value="salifert">沙里发</option></select><input type="number" id="records-nh3-number" min="0" max="100" step="any" inputmode="decimal" placeholder="读数"><div id="records-nh3-cards" class="records-cards" hidden></div><p id="records-nh3-note" class="records-note">益尔色卡尚未提供，先填数字。</p><output id="records-nh3-verdict"></output></div></div>
<div class="records-field"><div class="records-field-label"><span>NO2</span><span>mg/L</span></div><div class="records-control"><div id="records-no2-cards" class="records-cards"></div><button type="button" id="records-no2-between" class="records-between">介于0.1与0.5之间</button><div id="records-dilution" hidden><p class="records-note">原水到顶格：2mL桶水＋10mL RO水，再测稀释样。</p><span class="records-small-label">稀释样读数</span><div id="records-no2-diluted-cards" class="records-cards"></div><output id="records-dilution-result"></output></div></div></div>
<div class="records-field"><div class="records-field-label"><span>NO3</span><span>mg/L</span></div><div id="records-no3-cards" class="records-cards"></div></div>
<div class="records-numbers" id="records-numbers"></div>
</fieldset>
<fieldset class="records-actions"><legend>做了什么</legend><label for="records-ammonium">氯化铵水 · mL</label><div class="records-dose"><input id="records-ammonium" type="number" min="0" max="10000" step="any" inputmode="decimal" placeholder="没加就留空"><select id="records-ammonium-kind" aria-label="氯化铵水用途"><option value="initial">首剂</option><option value="feed">补喂</option><option value="check">检查量</option></select></div><p id="records-dose-note" class="records-note">只用于没有动物的养水期。</p>
<label for="records-biodigest">科迪 · 支</label><input id="records-biodigest" type="number" min="0" max="10000" step="1" inputmode="numeric" placeholder="没加就留空">
<label for="records-water">换水 · L</label><input id="records-water" type="number" min="0" max="10000" step="any" inputmode="decimal" placeholder="没换就留空">
<label for="records-prime">Prime · mL</label><input id="records-prime" type="number" min="0" max="10000" step="any" inputmode="decimal" placeholder="没加就留空">
<label for="records-note">备注</label><textarea id="records-note" rows="4" maxlength="2000" placeholder="观察、喂食、设备或其他情况"></textarea>
</fieldset></div><div class="records-save-row"><button id="records-submit" type="submit">保存到服务器</button><button id="records-cancel" type="button" hidden>取消修改</button><span id="records-save-status" role="status" aria-live="polite"></span></div></form></section>
<section class="records-latest"><div class="records-section-heading"><h2>最近读数</h2><span>各项分别显示最近测量时间</span></div><div id="records-latest"></div></section>
<section class="records-history" id="records-history-section"><div class="records-section-heading"><h2>历史记录</h2><span id="records-count"></span></div><div id="records-history"></div></section>
<details class="records-rules"><summary>颜色范围与剂量依据</summary><div id="records-rules"></div><p class="records-note">NH3按试剂的NH3／NH4读数记录，不表示游离氨。PO4暂时只记录，不自动分档。不同日期的测量不会拼成一次24小时检查；检查期间换水、加Prime或重复加氨，这轮不计。红黄绿用于状态提示，蓝色表示选中。</p></details>
</div></div>
<dialog id="records-login"><form id="records-login-form"><div class="records-dialog-heading"><h2 id="records-login-title">写入登录</h2><button type="button" id="records-login-close" aria-label="关闭">×</button></div><p id="records-login-description">输入写入密码。此浏览器会记住登录状态，密码不会保存在浏览器里。</p><label for="records-password">密码</label><input id="records-password" type="password" minlength="9" maxlength="128" autocomplete="current-password" required><div id="records-confirm-wrap" hidden><label for="records-password-confirm">再输入一次</label><input id="records-password-confirm" type="password" minlength="9" maxlength="128" autocomplete="new-password"></div><p id="records-login-error" role="status"></p><button id="records-login-submit" type="submit">登录</button></form></dialog>'''.replace('VERSION',VERSION)
    return site.shell('记录',body,'records.html',page='records',desc='检疫桶与主缸的水质、加药和换水记录',script=f'<script type="module" src="assets/records.js?v={VERSION}"></script>')
