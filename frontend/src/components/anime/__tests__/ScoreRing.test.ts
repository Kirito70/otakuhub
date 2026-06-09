import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreRing from '../ScoreRing.vue'

describe('ScoreRing', () => {
  it('renders score label', () => {
    const wrapper = mount(ScoreRing, { props: { score: 8.5 } })
    expect(wrapper.text()).toContain('8.5')
  })

  it('renders without label when showLabel is false', () => {
    const wrapper = mount(ScoreRing, { props: { score: 8.5, showLabel: false } })
    expect(wrapper.text()).toBe('')
  })

  it('hides label when showLabel is false', () => {
    const wrapper = mount(ScoreRing, { props: { score: 8.5, showLabel: false } })
    expect(wrapper.find('.score-label').exists()).toBe(false)
  })

  it('applies custom size', () => {
    const wrapper = mount(ScoreRing, { props: { score: 7.0, size: 48 } })
    const div = wrapper.find('.score-ring')
    expect(div.attributes('style')).toContain('48px')
  })

  it('renders SVG circles', () => {
    const wrapper = mount(ScoreRing, { props: { score: 9.2 } })
    expect(wrapper.find('svg').exists()).toBe(true)
    const circles = wrapper.findAll('circle')
    expect(circles.length).toBe(2) // bg + fill
  })
})
