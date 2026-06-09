import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SectionHeader from '../SectionHeader.vue'

describe('SectionHeader', () => {
  it('renders title', () => {
    const wrapper = mount(SectionHeader, { props: { title: 'Trending Now' } })
    expect(wrapper.text()).toContain('Trending Now')
  })
})
